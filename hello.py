# import list
from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import DataRequired
from datetime import datetime


# create a flask instance
app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"


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


# create a cusotm error


# invaild url
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Erro
@app.errorhandler(500)
def page_not_found(e):
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
        flash("Form submit succes")
    return render_template("nameinput.html", name=name, form=form)
