from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'  # Corrected tablename
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_instructor = db.Column(db.Boolean, default=False, nullable=False)
    
    enrollments = db.relationship('Enrollment', back_populates='student')
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, username, password, is_instructor=False):  # Fixed __init__ method
        self.username = username
        self.set_password(password)
        self.is_instructor = is_instructor
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def courses_enrolled(self):
        return [enrollment.course for enrollment in self.enrollments]

    @property
    def performance(self):
        return [{'course': enrollment.course.title, 'progress': enrollment.progress} for enrollment in self.enrollments]

class Course(db.Model):
    __tablename__ = 'course'  # Added tablename for clarity
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(500))
    
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    instructor = db.relationship('User', backref='courses')

    enrollments = db.relationship('Enrollment', back_populates='course', cascade="all, delete-orphan")
    assessments = db.relationship('Assessment', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    forums = db.relationship('Forum', backref='course', lazy='dynamic', cascade="all, delete-orphan")

class Enrollment(db.Model):
    __tablename__ = 'enrollment'  # Added tablename
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)
    
    student = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

class Assessment(db.Model):
    __tablename__ = 'assessment'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    
    questions = db.relationship('Question', backref='assessment', lazy='dynamic', cascade="all, delete-orphan")

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)

class Forum(db.Model):
    __tablename__ = 'forum'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    posts = db.relationship('Post', backref='forum', lazy='dynamic', cascade="all, delete-orphan")

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
