from app import db_instance
from datetime import datetime

class User(db_instance.Model):
    id = db_instance.Column(db_instance.Integer, primary_key = True)
    username = db_instance.Column(db_instance.String(64), index=True, unique=True)
    email = db_instance.Column(db_instance.String(120), index=True, unique=True)
    password_hash = db_instance.Column(db_instance.String(128))
    posts = db_instance.relationship("Post", backref="author", lazy="dynamic")

    def __repr__(self):                             # this method tells Python how to print objects of this class, which is going to be useful for debugging. 
        return "<User {}>".format(self.username)

class Post(db_instance.Model):
    id = db_instance.Column(db_instance.Integer, primary_key=True)
    body = db_instance.Column(db_instance.String(180))
    timestamp = db_instance.Column(db_instance.DateTime, index=True, default=datetime.utcnow)
    user_id = db_instance.Column(db_instance.Integer, db_instance.ForeignKey("user.id"))

    def __repr__(self):
        return "<Post {}".format(self.body)
