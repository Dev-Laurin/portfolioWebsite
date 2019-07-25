from flask_wtf import FlaskForm
from wtforms import Form, StringField, validators
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
	title = StringField('title', validators=[DataRequired()])
	date = StringField('date', validators=[DataRequired()])
	html = StringField('html', validators=[DataRequired()])

