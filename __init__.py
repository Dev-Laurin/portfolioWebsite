from flask import Flask, render_template, json, request, redirect
from werkzeug.utils import secure_filename
from flaskext.mysql import MySQL 
from datetime import datetime

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

#Flask config
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = "static/images/projects/"

#MySQL config
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = '' 
app.config['MYSQL_DATABASE_PASSWORD'] = '' 
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
@app.route("/makeProject", methods=["GET", "POST"])
def project(name=None): 
	print("here")
	if request.method == "POST": 
		print("post method")
		#Get form data 
		title = request.form.get('title', False) 
		desc = request.form.get('shortDescription', False)
		sDate = request.form.get('startDate', False) 
		eDate = request.form.get('endDate', False)

		#convert dates to mysql compatible format 
		sDate = datetime.strptime(sDate, '%b %d, %Y').strftime('%Y-%m-%d')
		eDate = datetime.strptime(eDate, '%b %d, %Y').strftime('%Y-%m-%d')

		print(request.form)

		print(title)
		print(desc)
		print(sDate)
		print(eDate)

		print("Got stuff, moving to image")

		#get image for project & upload it
		if 'file' not in request.files:
			print("file not in req.files")
			return redirect(request.url)

		file = request.files['file']
		print(file)

		#perhaps browser sent empty filename because user didn't upload
		if file.filename == '': 
			print("filename empty")
			return redirect(request.url)

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			#add project to database 
			cursor.execute("INSERT INTO project(title, body, start_date, end_date, short_description) VALUES (%s, 'Nothing', %s, %s, %s)", 
				(title, sDate, eDate, desc))
			conn.commit()
			print("upload successful?")

	return render_template('makeProject.html', name=name)	


from flask import send_from_directory
import os

@app.route('/js/world-110m.json')
def worldjson():
	filename = 'world-110m.json'
	root_dir = os.path.dirname(os.getcwd())
	return send_from_directory(os.path.join(root_dir, 'static', 'js'), filename)

if __name__ == "__main__": 
	app.run()
