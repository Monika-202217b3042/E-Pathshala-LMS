from flask import Flask
from config import DevelopmentConfig  # Adjust import according to your actual location
from .models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .routes import main  
    app.register_blueprint(main)

    return app
