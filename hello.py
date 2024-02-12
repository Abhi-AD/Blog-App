# import list
from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# create a flask instance
app = Flask(__name__)
# add the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

# secret  key for form validation
app.config["SECRET_KEY"] = "secretkey"


# create a model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    data_added = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return "<Name %r>" % self.name


# Create a Form Class User
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Form Class
class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


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


# route for user with dynamic name
@app.route("/user/<name>")
def user(name):
    return render_template("user.html", username=name)


# create a custom error


# invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


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


@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    our_users = Users.query.order_by(Users.data_added)  # Define our_users here
    if form.validate_on_submit():
        with app.app_context():  # Create an application context
            user = Users.query.filter_by(email=form.email.data).first()
            if user is None:
                user = Users(name=form.name.data, email=form.email.data)
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
    return render_template("add_user.html", form=form, name=name, our_users=our_users)


# Create database tables
with app.app_context():  # Create an application context
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
