class Config:
    SECRET_KEY = 'secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///epathshala.db'
    SQLALCHEMY_ECHO = True

class DevelopmentConfig(Config):
    DEBUG = True
