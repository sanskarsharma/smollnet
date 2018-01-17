from app import db_instance, login_manager_instance
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login_manager_instance

class User(UserMixin, db_instance.Model):
    id = db_instance.Column(db_instance.Integer, primary_key = True)
    username = db_instance.Column(db_instance.String(64), index=True, unique=True)
    email = db_instance.Column(db_instance.String(120), index=True, unique=True)
    password_hash = db_instance.Column(db_instance.String(128))
    posts = db_instance.relationship("Post", backref="author", lazy="dynamic")

    def __repr__(self):                             # this method tells Python how to print objects of this class, which is going to be useful for debugging. 
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash =  generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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
