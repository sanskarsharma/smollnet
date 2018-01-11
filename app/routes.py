from app import app_instance
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm

@app_instance.route('/')
@app_instance.route('/index')		# these are called decorators
def index():		# this is called a view function
	user = {"username": "sanskarssh"}
	posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
	return render_template("index.html", title = "bambadbonga", user = user, postslist = posts)



@app_instance.route('/login', methods = ["GET", "POST"])
def login():
	form_obj = LoginForm()
	if form_obj.validate_on_submit():
		flash("Login requested for user {} , remember me = {}".format(form_obj.username.data, form_obj.remember_me.data))
		return redirect(url_for("index"))
	return render_template("login.html", title= "Sign In", form = form_obj)
