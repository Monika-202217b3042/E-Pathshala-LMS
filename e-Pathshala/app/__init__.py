from flask import Flask  # type: ignore
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Added for migrations
from config import DevelopmentConfig
from .models import db, Course

migrate = Migrate()  # Initialize Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate with app and db

    with app.app_context():
        db.create_all()

    from .routes import main  
    app.register_blueprint(main)

    return app

def add_default_courses():
    """Function to add default courses to the database if none exist."""
    default_courses = [
        {'title': 'Python Programming', 'description': 'Learn Python from beginner to advanced.'},
        {'title': 'Data Science', 'description': 'Analyze data and derive insights.'},
        {'title': 'Web Development', 'description': 'Build engaging websites with HTML, CSS, and JavaScript.'}
    ]
    with db.session.begin():  # Ensures atomic transactions
        if Course.query.count() == 0:  # Only add if there are no courses
            for course_info in default_courses:
                course = Course(title=course_info['title'], description=course_info['description'])
                db.session.add(course)
