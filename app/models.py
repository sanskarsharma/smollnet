from app import db_instance, login_manager_instance, app_instance
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

import jwt
from time import time

followers = db_instance.Table("followers",
    db_instance.Column("follower_id", db_instance.Integer, db_instance.ForeignKey("user.id")),
    db_instance.Column("followed_id", db_instance.Integer, db_instance.ForeignKey("user.id")),
)

class User(UserMixin, db_instance.Model):
    id = db_instance.Column(db_instance.Integer, primary_key = True)
    username = db_instance.Column(db_instance.String(64), index=True, unique=True)
    email = db_instance.Column(db_instance.String(120), index=True, unique=True)
    password_hash = db_instance.Column(db_instance.String(128))
    
    about_me = db_instance.Column(db_instance.String(180))
    last_seen = db_instance.Column(db_instance.DateTime, default= datetime.utcnow)

    # relationships
    posts = db_instance.relationship("Post", backref="author", lazy="dynamic")
    followed = db_instance.relationship("User", secondary=followers,
        primaryjoin= (followers.c.follower_id==id),
        secondaryjoin= (followers.c.followed_id==id),
        backref = db_instance.backref("followers", lazy="dynamic"), 
        lazy="dynamic"
    )


    def __repr__(self):                             # this method tells Python how to print objects of this class, which is going to be useful for debugging. 
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash =  generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self,size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id==user.id).count() > 0
        
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    # to get list of Users who follow the logged in user, added later 
    # def get_followers(self):
    #      return User.query.join(followers,(followers.c.follower_id == User.id)).filter(
    #          followers.c.followed_id == self.id)
    # THE ABOVE METHOD WAS NOT NEEDED AS User CLASS HAS ALREADY BOTH followed AND follower(via backref) ATTRIBUTES

    def followed_posts(self):
        posts = Post.query.join(
            followers,(followers.c.followed_id == Post.user_id) ).filter(       # yha followers ko glti se double quotes me rka tha toh dimag ghas liye the apan
                followers.c.follower_id == self.id)
        # simplified : posts = Post.query.join(...).filter(...).order_by(...)
        # but we also want own posts in feed, hence first combine both then sort using order_by()
        own_posts = Post.query.filter_by(user_id= self.id)
        combined = posts.union(own_posts).order_by(Post.timestamp.desc())
        return combined


    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app_instance.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app_instance.config['SECRET_KEY'],algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
            
    
    



class Post(db_instance.Model):
    id = db_instance.Column(db_instance.Integer, primary_key=True)
    body = db_instance.Column(db_instance.String(180))
    timestamp = db_instance.Column(db_instance.DateTime, index=True, default=datetime.utcnow)
    user_id = db_instance.Column(db_instance.Integer, db_instance.ForeignKey("user.id"))

    def __repr__(self):
        return "<Post {}".format(self.body)

@login_manager_instance.user_loader
def load_user(id):
    return User.query.get(int (id))

