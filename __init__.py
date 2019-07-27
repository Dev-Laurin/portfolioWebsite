from flask import Flask, render_template, json, request, redirect
from werkzeug.utils import secure_filename
from flaskext.mysql import MySQL 
from datetime import datetime
from forms import PostForm #flask forms 
from bs4 import BeautifulSoup as bs #HTML Parsing
import uuid #Filename random generator
import base64 #base64 image decoding 
import re #substring search 

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

#Flask config
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = "static/images/projects/"

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

#Functions
def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(base64String):
	extension = re.search('/(.*);', base64String)
	filename = str(uuid.uuid4()) + "." + str(extension.group(1))
	src = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
	base64String = base64String.split(',')[1]
	with open(src, "wb") as fh: 
		fh.write(base64.b64decode(base64String.encode()))
		return src 

#Routing
@app.route("/")
def hello(name=None): 
	return render_template('index.html', name=name)

@app.route("/about")
def about(name=None): 
	return render_template('about.html', name=name)

@app.route("/projects")
def projects(name=None): 
	#call Python Procedure - GET all projects
	cursor.callproc('getAllProjects')
	data = cursor.fetchall()
	if len(data) is not 0: 
		conn.commit()

		#make a dictionary for easy frontend templating
		dd = []
		for d in data: 
			dict = {}
			dict['title'] = d[0]
			dict['body'] = d[1]
			dict['start_date'] = d[2]
			dict['end_date'] = d[3]
			dict['description'] = d[4]
			dd.append(dict)

		return render_template('projects.html', name=name, data=dd)
	else:
		return json.dumps({'error':str(data[0])})

@app.route("/interests")
def interests(name=None): 
	return render_template('interests.html', name=name)	

#POST requests 
app.config['SECRET_KEY'] = 'a really long secret key'
@app.route("/makePost", methods=["GET", "POST"])
def post(name=None):
	form = PostForm()
	if form.validate_on_submit(): 
		print('validated')

		if request.method == "POST": 
			#post 
			print("POST")
			#title 
			title = form.title.data 
			print(title)
			#original date
			date = form.date.data 
			date = datetime.strptime(date, '%b %d, %Y').strftime('%Y-%m-%d')
			print(date)
			#html body
			html = form.html.data 
			#parse images out of html 
			soup = bs(html, features="html.parser")
			images = soup.findAll('img')

			#upload images 
			for image in images: 
				image['src'] = upload_image(image['src'])

			#update image src changes
			html = str(soup)

			#add blog post to database 

			# cursor.execute("INSERT INTO blogPost(title, original_date, revised_date, html) VALUES (%s, %s, %s, %s)", 
			# 	(title, date, date, html))
			# conn.commit()

	return render_template('postForm.html', title='Post', form=form)


from flask import send_from_directory
import os

@app.route('/js/world-110m.json')
def worldjson():
	filename = 'world-110m.json'
	root_dir = os.path.dirname(os.getcwd())
	return send_from_directory(os.path.join(root_dir, 'static', 'js'), filename)

if __name__ == "__main__": 
	app.run()
