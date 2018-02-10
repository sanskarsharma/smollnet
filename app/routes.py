from app import app_instance, db_instance
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.models import User, Post
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
import time

from pyfcm import FCMNotification

@app_instance.route('/', methods=["GET", "POST"])
@app_instance.route('/index', methods=["GET","POST"])# these are called decorators
@login_required
def index():# this is called a view function
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db_instance.session.add(post)
        db_instance.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))

    page = request.args.get("page",1, type=int)
    posts = current_user.followed_posts().paginate(page,app_instance.config["POSTS_PER_PAGE"],False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title = "Home Page", postslist = posts.items, form=form, next_url=next_url,prev_url=prev_url)




@app_instance.route('/login', methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form_obj = LoginForm()

    if form_obj.validate_on_submit():
        user_obj = User.query.filter_by(username = form_obj.username.data).first()
        if user_obj is None or not user_obj.check_password(password = form_obj.password.data):
            flash("Invalid usernae or password")
            return redirect(url_for("login"))
        login_user( user_obj, remember  = form_obj.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title= "Sign In", form = form_obj)

@app_instance.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app_instance.route("/register", methods=["GET", "POST"])
def register_user():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    registrattion_form_obj = RegistrationForm()
    if registrattion_form_obj.validate_on_submit():     # yha pe () ni lgaya tha tune or bht irrelevent error mila tha. python also fails silently at times
        user_obj = User(username = registrattion_form_obj.username.data, email = registrattion_form_obj.email_addr.data)
        user_obj.set_password(registrattion_form_obj.password.data)
        db_instance.session.add(user_obj)
        db_instance.session.commit()
        flash("Congratulations, you have been registered")
        return redirect(url_for("login"))
    return render_template("register.html", title = "Register yourself", form = registrattion_form_obj)


@app_instance.route("/user/<username>")
@login_required
def user_profile(username):
    user_obj = User.query.filter_by(username= username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user_obj.posts.order_by(Post.timestamp.desc()).paginate(
        page, app_instance.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user_profile', username=user_obj.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user_profile', username=user_obj.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("user_profile.html", user = user_obj, posts = posts.items, next_url=next_url,prev_url=prev_url)


# using this functionality to add last seen feature in our app, whenever a user sends any request it records time
@app_instance.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db_instance.session.commit()


@app_instance.route("/edit_profile", methods=["GET", "POST"] )
@login_required
def edit_profile():
    edit_profile_form = EditProfileForm(orig_username= current_user.username)
    if edit_profile_form.validate_on_submit():
        current_user.username = edit_profile_form.username.data
        current_user.about_me = edit_profile_form.about_me.data
        db_instance.session.commit()
        flash("Your changes have been saved")
        return redirect(url_for("user_profile", username=current_user.username))
    elif request.method == "GET":
        edit_profile_form.username.data = current_user.username
        if current_user.about_me:
            edit_profile_form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title = "Edit Profile", form = edit_profile_form)

# @app_instance.route("/fcm", methods=["GET"])
# @login_required
# def send_fcm():
#     push_service = FCMNotification(api_key="AAAAbEgDzzU:APA91bEkITOc5PMGLwAwyoUtMFF7vCcNBikr30eUW6HglasaSBdqtQEzb9NtKR_fZrVY-yw0ZicDdeSi7ptWKpB_tcxVTX_a55EFgXg-_MgoqQn8uGcrad4jHr_eNvKzgBkFB6cPp45A")
#     # OR initialize with proxies

#     proxy_dict = {
            
#             }
#     push_service = FCMNotification(api_key="AAAAbEgDzzU:APA91bEkITOc5PMGLwAwyoUtMFF7vCcNBikr30eUW6HglasaSBdqtQEzb9NtKR_fZrVY-yw0ZicDdeSi7ptWKpB_tcxVTX_a55EFgXg-_MgoqQn8uGcrad4jHr_eNvKzgBkFB6cPp45A", proxy_dict=proxy_dict)

#     # Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging

#     registration_id = "fB5hluUNGlg:APA91bFJz5kkoTLpZF6giEW3hnpU_Q4MMqkQwVrUI7SB8BOyfT0k_v2CimFEuoZXm9AHsg8y5KF-O2dEfOBuqt6Rqb6OFR7sN-eV6moy0FOcOwpJf9Kv2DynI1da77E3hXtiDNJpv43N"
#     message_title = "Update in Schedule"
#     message_body = "Schedule updated for FINALE"


#     data_message ={"title" : "The da vinci code",
#     "description" : "wfwgf wfwefwgbiwgwigubwigi wugwiugwuig",
#     "timestamp" : str(int(time.time())),
#     "author": "issued by Sanskar"}

#     #result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
#     result = push_service.notify_single_device(registration_id=registration_id, message_body=message_body, data_message=data_message)
#     print(result)
#     print("\n\n")

#     return render_template("index.html")

############# project resumed on 10022018  ###############

@app_instance.route("/follow/<username>")
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user_profile', username=username))

    current_user.follow(user)
    db_instance.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user_profile', username=username))

@app_instance.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user_profile', username=username))
    current_user.unfollow(user)
    db_instance.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user_profile', username=username))

@app_instance.route("/explore")
@login_required
def explore():
    page = request.args.get("page",1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app_instance.config['POSTS_PER_PAGE'], False)    
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore', postslist=posts.items, next_url=next_url,prev_url=prev_url)

