from flask import Flask, render_template, json
from flaskext.mysql import MySQL 

#Flask config
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

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
