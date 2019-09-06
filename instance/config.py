
#DB config 
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://webdev:shulkAssistant50%@localhost/site'
SQLALCHEMY_TRACK_MODIFICATIONS = False 

#Flask config
import os 
SECRET_KEY = os.urandom(16)
TEMPLATES_AUTO_RELOAD = True
UPLOAD_FOLDER = "static/uploads/"

#Flask Uploads config
UPLOADED_IMAGES_DEST = 'static/uploads/images/'
UPLOADED_DOCUMENTS_DEST = 'static/uploads/documents/'
UPLOADED_TEXT_DEST = 'static/uploads/text/'