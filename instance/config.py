
#DB config 
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://webdev:shulkAssistant50%@localhost/site'
SQLALCHEMY_TRACK_MODIFICATIONS = False 
SQLALCHEMY_ECHO = False

#Flask config
import os 
SECRET_KEY = "alkasjdlfkdjsdfdslkjlkjl;kjl;kjfd"
DEBUG = True 
TEMPLATES_AUTO_RELOAD = True
from pathlib import Path 
UPLOAD_FOLDER = Path.cwd().joinpath("website", "portfolioWebsite", "blog", "static")

#Flask uploads 
ALLOWED_EXTENSIONS = ["jpg", "png"]
MAX_CONTENT_LENGTH = 1000 * 1024 * 1024 #1000mb 

#Flask User
USER_APP_NAME = "blog"
USER_ENABLE_EMAIL = False 
USER_ENABLE_USERNAME = True 
USER_EMAIL_SENDER_NAME = USER_APP_NAME
USER_EMAIL_SENDER_EMAIL = "noreply@de-laurian.rocks"
USER_ENABLE_REGISTER = False 

#Upload images in html 
UPLOAD_FOLDER_MANUAL = Path.cwd().joinpath("website", "portfolioWebsite", "blog", "static", "uploads", "images")
UPLOADED_IMAGES_DEST = '/static/uploads/images/'
UPLOADED_DOCUMENTS_DEST = '/static/uploads/documents/'