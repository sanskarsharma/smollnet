from app import app_instance, db_instance
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post, BaseEntity, EntityComments, EntityLikes
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
import time
import json
from pyfcm import FCMNotification

from app.email import send_password_reset_email

@app_instance.route('/', methods=["GET", "POST"])
@app_instance.route('/index', methods=["GET","POST"])# these are called decorators
@login_required
def index():# this is called a view function
    form = PostForm()
    if form.validate_on_submit():
        base_entity = BaseEntity()
        db_instance.session.add(base_entity)
        db_instance.session.commit()
        db_instance.session.refresh(base_entity)

        post = Post(body=form.post.data, author=current_user, entity_id=base_entity.id)
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
    return render_template("user_profile.html", user = user_obj, postslist = posts.items, next_url=next_url,prev_url=prev_url, title=user_obj.username + "'s profile")


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


@app_instance.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app_instance.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db_instance.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app_instance.route("/test", methods=["POST","GET"])
def testing():
    return "jquery works like charm"



@app_instance.route("/user/<username>/followers")
@login_required
def get_followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    # followers = user.get_followers()
    # we already have a followers attribute of user class via backref, dumb cunt.
    return render_template("followers_following.html", person=user, heading="followers")

@app_instance.route("/user/<username>/following")
@login_required
def get_following(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("followers_following.html", person=user, heading="following")


""" ------------------------ APIS for enabling comments below ------------------"""

@app_instance.route("/post/<id>")
@login_required
def post_details(id):
    post = Post.query.filter_by(id=id).first_or_404()
    return render_template("post_detail.html", post=post, title=post.author.username + "'s post")


@app_instance.route("/entity/<id>/like")
@login_required
def entity_like(id):
    base_entity = BaseEntity.query.get(id)
    liked = False
    if base_entity.is_liked_by(current_user):
        base_entity.unlike(current_user)
    else:
        base_entity.like(current_user)
        liked = True

    response_dict = {}
    response_dict["message"] = "OK"
    response_dict["liked"] = liked
    response_dict["likes_count"] = base_entity.likes_count()

    return json.dumps(response_dict)

