#globals.py
from flask_uploads import UploadSet, configure_uploads, IMAGES, TEXT, DOCUMENTS, patch_request_class

#uploads
images = UploadSet('images', IMAGES)
text = UploadSet('text', TEXT)
documents = UploadSet('documents', DOCUMENTS)

ALLOWED_EXTENSIONS = images
