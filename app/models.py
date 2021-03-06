from app import db, login
from flask import current_app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt
from sqlalchemy.orm import backref


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    clinics = db.relationship('Clinic', backref='author', lazy='dynamic')
    persons = db.relationship('Person', backref='author', lazy='dynamic')
    visits = db.relationship('Visit', backref='author', lazy='dynamic')
    tenders = db.relationship('Tender', backref='author', lazy='dynamic')
    contracts = db.relationship('Contract', backref='author', lazy='dynamic')
    arch_contracts = db.relationship('ContractArchive', backref='author', lazy='dynamic')
    forget = db.relationship('DoNotForget', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(240))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Region(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(180), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    clinics = db.relationship('Clinic')
    persons = db.relationship('Person')

class Clinic(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    clinic_name = db.Column(db.String(180), index=True, unique=True)
    address = db.Column(db.String(250), index=True)
    inn = db.Column(db.String(15), nullable=False, unique=True)
    region_name = db.Column(db.String(180), db.ForeignKey('region.name'))
    comments = db.Column(db.String(250), index=True)
    persons = db.relationship('Person', lazy='dynamic', cascade="all,delete", backref="parent")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Person(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(250), index=True)
    comments = db.Column(db.String(250), index=True)
    picture_filename = db.Column(db.String(250), nullable=True)
    picture_url = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(180), index=True, unique=True)
    department = db.Column(db.String(100), index=True)
    last_visit = db.Column(db.DateTime)
    next_visit = db.Column(db.DateTime)
    date_of_request = db.Column(db.DateTime)
    date_of_request2 = db.Column(db.DateTime)
    region_name = db.Column(db.String(180), db.ForeignKey('region.name'))
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    visits = db.relationship('Visit', lazy='dynamic')

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime, nullable=False)
    date_of_next_visit = db.Column(db.DateTime, nullable=False)
    arrangements = db.Column(db.String(250), index=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Tender(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    number = db.Column(db.String(30), unique=True)
    customer = db.Column(db.String(100), index=True)
    end_date = db.Column(db.DateTime)
    game_date = db.Column(db.DateTime)
    ground = db.Column(db.String(100), index=True)
    company = db.Column(db.String(100), index=True)
    notes = db.Column(db.String(250), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    company = db.Column(db.String(100), index=True)
    ground = db.Column(db.String(100), index=True)
    customer = db.Column(db.String(100), index=True)
    number = db.Column(db.String(50), unique=True)
    sign_date = db.Column(db.DateTime)
    supply = db.Column(db.String(20), unique=True)
    notes = db.Column(db.String(250), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class ContractArchive(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    company = db.Column(db.String(100), index=True)
    ground = db.Column(db.String(100), index=True)
    customer = db.Column(db.String(100), index=True)
    number = db.Column(db.String(50))
    sign_date = db.Column(db.DateTime)
    supply = db.Column(db.String(20), unique=True)
    notes = db.Column(db.String(250), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class DoNotForget(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    notes = db.Column(db.String(250), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#class Product(db.Model):
    #id = db.Column(db.Integer, primary_key = True)
    #group = db.Column(db.String(80), nullable=False)
    #vendor = db.Column(db.String(80), nullable=False)
    #nomenclature = db.Column(db.String(80), nullable=False)
    #enlgish = db.Column(db.String(250), nullable=False)
    #price = db.Column(db.String(20), nullable=False)
    #reg = db.Column(db.String(20), nullable=False)
    #RU = db.relationship('RU', backref=backref("children", cascade="all,delete"))

#class RU(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    #url = db.Column(db.String(50), nullable=False)
    #name = db.Column(db.String(20), db.ForeignKey('product.reg', ondelete='CASCADE'))
