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



@login_manager_instance.user_loader
def load_user(id):
    return User.query.get(int (id))


""" ------------------ new models below - likes comments etc ---------- """


class TimeStampedModel(db_instance.Model):
    __abstract__ = True

    created_on = db_instance.Column(db_instance.DateTime, default=db_instance.func.now())
    updated_on = db_instance.Column(db_instance.DateTime, default=db_instance.func.now(), onupdate=db_instance.func.now())


class BaseEntity(TimeStampedModel):
    __tablename__ = 'base_entity'

    id = db_instance.Column(db_instance.Integer, primary_key=True)

    def is_liked_by(self, user):
        liked = EntityLikes.query.filter_by(user_id=user.id, entity_id=self.id).first()
        return True if liked is not None else False

    def like(self, user):
        like = EntityLikes(user_id=user.id, entity_id=self.id)
        db_instance.session.add(like)
        db_instance.session.commit()

    def unlike(self, user):
        like = EntityLikes.query.filter_by(entity_id=self.id, user_id=user.id).first()
        db_instance.session.delete(like)
        db_instance.session.commit()

    def likes_count(self):
        return EntityLikes.query.filter_by(entity_id=self.id).count()

    def likers(self):
        return User.query.join(EntityLikes, User.id == EntityLikes.user_id).all()


class EntityLikes(TimeStampedModel):
    __tablename__ = 'entity_likes'

    id = db_instance.Column(db_instance.Integer, primary_key=True)
    user_id = db_instance.Column(db_instance.Integer, db_instance.ForeignKey("user.id"))
    entity_id = db_instance.Column(db_instance.Integer, db_instance.ForeignKey("base_entity.id"))

    def __repr__(self):
        return "<EntityLikes {} likes {}>".format(self.user_id, self.entity_id)




class EntityComments(TimeStampedModel):
    __tablename__ = 'entity_comments'

    _N = 6

    id = db_instance.Column(db_instance.Integer, primary_key=True)
    entity_id = db_instance.Column(db_instance.Integer, db_instance.ForeignKey("base_entity.id")) # analogous to post_id for our case
    text = db_instance.Column(db_instance.Text)
    user_id = db_instance.Column(db_instance.Integer, db_instance.ForeignKey("user.id"))
    path = db_instance.Column(db_instance.Text)
    parent_id = db_instance.Column(db_instance.Integer, db_instance.ForeignKey('entity_comments.id'))
    replies = db_instance.relationship(
        'EntityComments', backref=db_instance.backref('parent', remote_side=[id]),
        lazy='dynamic')

    def save(self):
        db_instance.session.add(self)
        db_instance.session.commit()
        prefix = self.parent.path + '.' if self.parent else ''
        self.path = prefix + '{:0{}d}'.format(self.id, self._N)
        db_instance.session.commit()

    def level(self):
        return len(self.path) // self._N - 1


class BigPost(TimeStampedModel):
    __tablename__ = 'big_post'

    id = db_instance.Column(db_instance.Integer, primary_key=True)
    entity_id = db_instance.Column(db_instance.Integer, db_instance.ForeignKey("base_entity.id"))
    user_id = db_instance.Column(db_instance.Integer, db_instance.ForeignKey("user.id"))

    title = db_instance.Column(db_instance.String(180))
    body = db_instance.Column(db_instance.Text)

    def __repr__(self):
        return "<BigPost {}>".format(self.title)


class Post(db_instance.Model):
    id = db_instance.Column(db_instance.Integer, primary_key=True)
    body = db_instance.Column(db_instance.String(180))
    timestamp = db_instance.Column(db_instance.DateTime, index=True, default=datetime.utcnow)
    user_id = db_instance.Column(db_instance.Integer, db_instance.ForeignKey("user.id"))
    entity_id = db_instance.Column(db_instance.Integer, db_instance.ForeignKey("base_entity.id"), unique=True) # unique for one-to-one reltnshp

    entity = db_instance.relationship("BaseEntity", backref="post")

    def __repr__(self):
        return "<Post {} -eid-{}>".format(self.body, self.entity_id)
