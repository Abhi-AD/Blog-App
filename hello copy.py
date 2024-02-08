from flask import Flask, render_template

# create a flask instance
app = Flask(__name__)


# create a route decorator
@app.route("/")
def home():
    first_name = "Abhishek"
    last_name = "Dangi"
    stuff = "This is some <strong>random</strong> text."
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
