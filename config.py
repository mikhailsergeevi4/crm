import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['mikhailsergeevi4@yandex.ru']

    UPLOAD_FOLDER = 'images/'
    UPLOADS_DEFAULT_DEST = os.path.join(basedir, 'images/')
    UPLOADS_DEFAULT_URL = 'images/'

    UPLOADED_IMAGES_DEST = os.path.join(basedir, 'images/')
    UPLOADED_IMAGES_URL = 'images/'

    POSTS_PER_PAGE = 10
    CLINICS_PER_PAGE = 25
