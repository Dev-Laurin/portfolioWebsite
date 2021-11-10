#uploadFunctions.py
import re #substring search
import uuid #Filename random generator
import base64 #base64 image decoding 
import os 
from flask import current_app, g
from werkzeug.utils import secure_filename

#Image processing for mobile
from PIL import Image

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(base64String):
	extension = re.search('/(.*);', base64String)
	filename = str(uuid.uuid4()) + "." + str(extension.group(1))
	src = os.path.join(current_app.config['UPLOAD_FOLDER_MANUAL'], secure_filename(filename))
	base64String = base64String.split(',')[1]
	fh = open(src, "wb")
	fh.write(base64.b64decode(base64String.encode()))
	fh.close()
	src = os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], secure_filename(filename))
	return src 

def create_thumbnail(path, filename):
	size = (128, 128)

	image = Image.open(path)
	new_image = image.copy()
	new_image.thumbnail(size)
	#rename
	split_name = os.path.splitext(filename)
	new_filename = split_name[0] + "_thumbnail." + split_name[1]
	new_filename = os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], secure_filename(new_filename))
	new_image.save(new_filename)
