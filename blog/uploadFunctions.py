#uploadFunctions.py

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(base64String):
	extension = re.search('/(.*);', base64String)
	filename = str(uuid.uuid4()) + "." + str(extension.group(1))
	src = os.path.join(app.config['UPLOADED_IMAGES_DEST'], secure_filename(filename))
	base64String = base64String.split(',')[1]
	with open(src, "wb") as fh: 
		fh.write(base64.b64decode(base64String.encode()))
		return src 
