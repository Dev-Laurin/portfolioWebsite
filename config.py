#config.py
from flask import Flask
from flaskext.mysql import MySQL 
from flask_uploads import UploadSet, configure_uploads, IMAGES, TEXT, DOCUMENTS, patch_request_class

from globals import images, text, documents, ALLOWED_EXTENSIONS

#Flask config
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a really long secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = "static/uploads/"

#Flask Uploads config
app.config['UPLOADED_IMAGES_DEST'] = 'static/uploads/images/'
app.config['UPLOADED_DOCUMENTS_DEST'] = 'static/uploads/documents/'
app.config['UPLOADED_TEXT_DEST'] = 'static/uploads/text/'
configure_uploads(app, (images, text, documents))
patch_request_class(app, 50 * 1024 * 1024) #50 MB max file upload

#MySQL config
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'webdev' 
app.config['MYSQL_DATABASE_PASSWORD'] = 'shulkAssistant50%' 
app.config['MYSQL_DATABASE_DB'] = 'site'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#MySQL connection 
conn = mysql.connect()
cursor = conn.cursor()