from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_instructor = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, is_instructor=False):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.is_instructor = is_instructor

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    instructor = db.relationship('User', backref=db.backref('courses', lazy=True))
