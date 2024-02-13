# -----------------------------------------------------------------------------------------
# -----------------------------------------import list----------------------------------
# -----------------------------------------------------------------------------------------
from flask import Flask, render_template, flash,request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash







# -----------------------------------------------------------------------------------------
# -----------------------------------------Database----------------------------------
# -----------------------------------------------------------------------------------------

# create a flask instance
app = Flask(__name__)
# add the database
# # odd SQlITE DB
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
# New DB
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/flaskcrud"
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# secret  key for form validation
app.config["SECRET_KEY"] = "secretkey"







# -----------------------------------------------------------------------------------------
# -----------------------------------------HomPages----------------------------------
# -----------------------------------------------------------------------------------------


# create a route decorator
@app.route("/")
def home():
    first_name = "Abhishek"
    last_name = "Dangi"
    stuff = "This is some <strong>random</strong> text."
    flash("Welcome to Flask Blog App")
    dict_fruit = ["mango", "apple", "orange", 13]
    return render_template(
        "index.html",
        firstname=first_name,
        lastname=last_name,
        Stuff=stuff,
        dictfruit=dict_fruit,
    )



# -----------------------------------------------------------------------------------------
# -----------------------------------------Custome Error ----------------------------------
# -----------------------------------------------------------------------------------------

# invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500





# -----------------------------------------------------------------------------------------
# -----------------------------------------Users Name----------------------------------
# -----------------------------------------------------------------------------------------

# route for user with dynamic name
@app.route("/user/<name>")
def user(name):
    return render_template("user.html", username=name)


# Create a Form Class
class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")
   


# Create Name Page
@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    form = NameForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash("Form submit success")
    return render_template("nameinput.html", name=name, form=form)











# -----------------------------------------------------------------------------------------
# -----------------------------------------Users Database----------------------------------
# -----------------------------------------------------------------------------------------


# create a model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    favorite_color = db.Column(db.String(100))
    data_added = db.Column(db.DateTime, default=datetime.utcnow())
    # do some password
    password_hash = db.Column(db.String(255))
    
    @property
    def password(self):
        raise AttributeError('Password is not a Readable Attribute!')
    
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password) 

    def __repr__(self):
        return "<Name %r>" % self.name






# Create a Form Class User
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    submit = SubmitField("Submit")


@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    our_users = Users.query.order_by(Users.data_added)  # Define our_users here
    if form.validate_on_submit():
        with app.app_context():  # Create an application context
            user = Users.query.filter_by(email=form.email.data).first()
            if user is None:
                user = Users(name=form.name.data, email=form.email.data, favorite_color = form.favorite_color.data)
                db.session.add(user)
                db.session.commit()
                flash("User Added Successfully!")
                # Refresh the users list after adding a new user
                our_users = Users.query.order_by(Users.data_added)
            else:
                flash("User already exists!")
            name = form.name.data
            form.name.data = ""
            form.email.data = ""
            form.favorite_color.data = ""
    return render_template("add_user.html", form=form, name=name, our_users=our_users)




# Update DB user
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User update Succesfully!")
            return render_template("user_update.html", form=form, name_to_update=name_to_update)
        except:
            flash("Error ! Please check your data.")
            return render_template("user_update.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("user_update.html", form=form, name_to_update=name_to_update, id=id)
            



# delete DB user
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User delete successfully!")
        our_users = Users.query.order_by(Users.name).all()
        return render_template("add_user.html", form=form, name=name, our_users=our_users)
        
    except:
        flash("Opps! something error !")
        return render_template("add_user.html", form=form, name=name, our_users=our_users)












# Create database tables
with app.app_context():  # Create an application context
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
