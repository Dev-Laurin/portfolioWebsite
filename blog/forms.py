from flask_wtf import FlaskForm
from wtforms import (Form, StringField, BooleanField, 
	TextAreaField, validators, widgets, 
	SelectMultipleField, PasswordField
	)
from wtforms.validators import DataRequired, Length, InputRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import (UploadSet, 
	configure_uploads, IMAGES, TEXT, 
	DOCUMENTS
)
images = UploadSet('images', IMAGES)

class PostForm(FlaskForm):
	title = StringField('title', validators=[DataRequired()])
	date = StringField('date', validators=[DataRequired()])
	image = FileField('file', validators=[FileAllowed(images, 'Images only!')])
	isProject = BooleanField('isProject')
	html = TextAreaField('html', validators=[DataRequired()])

class LoginForm(FlaskForm):
	username = StringField('username', validators=[DataRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])