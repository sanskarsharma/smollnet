from app import app_instance
from flask import render_template

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
