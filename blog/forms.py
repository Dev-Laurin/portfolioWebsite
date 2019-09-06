from flask_wtf import FlaskForm
from wtforms import (Form, StringField, BooleanField, 
	TextAreaField, validators, widgets, 
	SelectMultipleField
	)
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import (UploadSet, 
	configure_uploads, IMAGES, TEXT, 
	DOCUMENTS, patch_request_class
)
images = UploadSet('images', IMAGES)

class PostForm(FlaskForm):
	title = StringField('title', validators=[DataRequired()])
	date = StringField('date', validators=[DataRequired()])
	image = FileField('file', validators=[FileAllowed(images, 'Images only!')])
	isProject = BooleanField('isProject')
	html = TextAreaField('html', validators=[DataRequired()])