from flask_wtf import FlaskForm
from wtforms import Form, StringField, BooleanField, TextAreaField, validators, widgets, SelectMultipleField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from config import images, cursor, conn 

class MultiCheckboxField(SelectMultipleField):
	widget = widgets.ListWidget(prefix_label=False)
	option_widget = widgets.CheckboxInput()

class PostForm(FlaskForm):
	title = StringField('title', validators=[DataRequired()])
	date = StringField('date', validators=[DataRequired()])
	image = FileField('file', validators=[FileAllowed(images, 'Images only!')])
	isProject = BooleanField('isProject')
	html = TextAreaField('html', validators=[DataRequired()])
	
	#Tags / checkboxes 
	#call Python Procedure - GET all projects
	cursor.callproc('getAllTags')
	data = cursor.fetchall()
	if len(data) is not 0: 
		conn.commit()
		tags = []
		for d in data: 
			tags.append(d[1])

	tags = MultiCheckboxField('Tags', choices=tags)
