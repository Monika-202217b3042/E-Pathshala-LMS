from flask import Flask # type: ignore
from config import DevelopmentConfig  # Adjust import according to your actual location
from .models import db, Course

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .routes import main  
    app.register_blueprint(main)

    return app

def add_default_courses():
    default_courses = [
        {'title': 'Python Programming', 'description': 'Learn Python from beginner to advanced.'},
        {'title': 'Data Science', 'description': 'Analyze data and derive insights.'},
        {'title': 'Web Development', 'description': 'Build engaging websites with HTML, CSS, and JavaScript.'}
    ]
    if Course.query.count() == 0:  # Only add if there are no courses
        for course_info in default_courses:
            course = Course(title=course_info['title'], description=course_info['description'])
            db.session.add(course)
        db.session.commit()