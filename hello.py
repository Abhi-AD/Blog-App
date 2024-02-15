# -----------------------------------------------------------------------------------------
# -----------------------------------------import list----------------------------------
# -----------------------------------------------------------------------------------------
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    BooleanField,
    ValidationError,
)
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea


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
migrate = Migrate(app, db)

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
    return render_template("Custom Error/404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("Custom Error/500.html"), 500


# -----------------------------------------------------------------------------------------
# -----------------------------------------Users Name----------------------------------
# -----------------------------------------------------------------------------------------


# route for user with dynamic name
@app.route("/user/<name>")
def user(name):
    return render_template("Users Name/user.html", username=name)


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
    return render_template("Users Name/nameinput.html", name=name, form=form)


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
        raise AttributeError("Password is not a Readable Attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<Name %r>" % self.name


# Create a Form Class User
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField(
        "Password",
        validators={
            DataRequired(),
            EqualTo("password_hash2", message="Passwords must match."),
        },
    )
    password_hash2 = PasswordField(" Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# add user
@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    our_users = Users.query.order_by(Users.data_added)  # Define our_users here
    if form.validate_on_submit():
        with app.app_context():  # Create an application context
            user = Users.query.filter_by(email=form.email.data).first()
            if user is None:
                # hash password using pbkdf2:sha256
                hashed_pw = generate_password_hash(
                    form.password_hash.data, method="pbkdf2:sha256"
                )

                user = Users(
                    name=form.name.data,
                    email=form.email.data,
                    favorite_color=form.favorite_color.data,
                    password_hash=hashed_pw,
                )
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
            form.password_hash.data = ""
    return render_template(
        "Users/add_user.html", form=form, name=name, our_users=our_users
    )


# Update DB user
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        try:
            db.session.commit()
            flash("User update Succesfully!")
            return render_template(
                "Users/user_update.html",
                form=form,
                name_to_update=name_to_update,
                id=id,
            )
        except:
            flash("Error ! Please check your data.")
            return render_template(
                "Users/user_update.html",
                form=form,
                name_to_update=name_to_update,
                id=id,
            )
    else:
        return render_template(
            "Users/user_update.html", form=form, name_to_update=name_to_update, id=id
        )


# delete DB user
@app.route("/delete/<int:id>")
def delete(id):
    post_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("User delete successfully!")
        our_users = Users.query.order_by(Users.name)
        return render_template(
            "Users/add_user.html", form=form, name=name, our_users=our_users
        )

    except:
        flash("Opps! something error !")
        return render_template(
            "Users/add_user.html", form=form, name=name, our_users=our_users
        )


# Create a Form Class
class PasswordForm(FlaskForm):
    email = StringField("What is your email?", validators=[DataRequired()])
    password_hash = PasswordField("What is your password?", validators=[DataRequired()])
    submit = SubmitField("Submit")


# password check
@app.route("/test_password", methods=["GET", "POST"])
def test_password():
    email = None
    password = None
    password_to_check = None
    passed = None
    form = PasswordForm()
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ""
        form.password_hash.data = ""
        # lookup user email address
        password_to_check = Users.query.filter_by(email=email).first()
        # check hashes password
        if password_to_check is not None:
            passed = check_password_hash(password_to_check.password_hash, password)
        else:
            passed = False  # Or any other appropriate action
        # passed = check_password_hash(password_to_check.password_hash, password)
    return render_template(
        "Users/test_password.html",
        email=email,
        password=password,
        form=form,
        passed=passed,
        password_to_check=password_to_check,
    )


# -----------------------------------------------------------------------------------------
# -----------------------------------------JSON Things----------------------------------
# -----------------------------------------------------------------------------------------
@app.route("/date")
def get_current_date():
    favorite_pizza = {
        "name": "Vegan Veggie",
        "name1": "Baby Bell Peppers",
        "name2": "Daiya Vegan Mozzarella",
        "name3": "Oregano",
    }

    return favorite_pizza
    # return {"Date": date.today()}


# -----------------------------------------------------------------------------------------
# -----------------------------------------Posts----------------------------------
# -----------------------------------------------------------------------------------------


# Create a database
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    author = db.Column(db.String(100))
    data_added = db.Column(db.DateTime, default=datetime.utcnow())
    slug = db.Column(db.String(255))


#  create a form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField()


# Add Post Pages
@app.route("/add_post", methods=["GET", "POST"])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(
            title=form.title.data,
            content=form.content.data,
            author=form.author.data,
            slug=form.slug.data,
        )
        form.title.data = ""
        form.content.data = ""
        form.author.data = ""
        form.slug.data = ""

        db.session.add(post)
        db.session.commit()
        flash("Blog Posts Submitted Successfully!")
    return render_template("Posts/add_post.html", form=form)


# all view
@app.route("/posts")
def posts():
    posts = Posts.query.order_by(Posts.data_added)
    return render_template("Posts/posts.html", posts=posts)


# current view
@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("Posts/post.html", post=post)


# update post
@app.route("/update_post/<int:id>", methods=["GET", "POST"])
def update_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Update!")
        return redirect(url_for("post", id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template("Posts/update_post.html", form=form, post=post)


# update post
@app.route("/delete_post/<int:id>")
def delete_post(id):
    form = PostForm()
    post_to_delete = Posts.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Posts delete successfully!")
        posts = Posts.query.order_by(Posts.data_added)
        return render_template("Posts/add_post.html", form=form, posts=posts)
    except:
        flash("Opps! something error !")
        posts = Posts.query.order_by(Posts.data_added)
        return render_template("Posts/add_post.html", form=form, posts=posts)


# Create database tables
with app.app_context():  # Create an application context
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
