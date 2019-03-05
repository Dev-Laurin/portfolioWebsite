from flask import Flask
from flask import render_template 
app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/")
def hello(name=None): 
	return render_template('index.html', name=name)

@app.route("/about")
def about(name=None): 
	return render_template('about.html', name=name)

@app.route("/projects")
def projects(name=None): 
	return render_template('projects.html', name=name)


from flask import send_from_directory
import os

@app.route('/js/world-110m.json')
def worldjson():
	filename = 'world-110m.json'
	root_dir = os.path.dirname(os.getcwd())
	return send_from_directory(os.path.join(root_dir, 'static', 'js'), filename)

if __name__ == "__main__": 
	app.run()
