from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_instructor = db.Column(db.Boolean, default=False)
    enrollments = db.relationship('Enrollment', back_populates='student')
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    

    def __init__(self, username, password, is_instructor=False):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.is_instructor = is_instructor
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    instructor = db.relationship('User', backref='courses')
    enrollments = db.relationship('Enrollment', back_populates='course')
    assessments = db.relationship('Assessment', backref='course', lazy='dynamic')
    forums = db.relationship('Forum', backref='course', lazy='dynamic')
    
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    progress = db.Column(db.Integer)  # e.g., 0 to 100 representing percentage complete
    student = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    title = db.Column(db.String(100))
    questions = db.relationship('Question', backref='assessment', lazy='dynamic')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'))
    text = db.Column(db.String(255))
    correct_answer = db.Column(db.String(255))

class Forum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    posts = db.relationship('Post', backref='forum', lazy='dynamic')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))