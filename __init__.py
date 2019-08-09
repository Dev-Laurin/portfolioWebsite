from flask import Flask, url_for, render_template, json, request, redirect
from werkzeug.utils import secure_filename
from datetime import datetime
from forms import PostForm #flask forms 
from bs4 import BeautifulSoup as bs #HTML Parsing
import uuid #Filename random generator
import base64 #base64 image decoding 
import re #substring search 

from config import images, text, documents, app, conn, cursor #our custom flask configurations
from forms import PostForm 
from uploadFunctions import allowed_file, upload_image #our custom functions

@app.route("/", methods=["GET"])
def hello(name=None): 
	return render_template('index.html', name=name)

@app.route("/about", methods=["GET"])
def about(name=None): 
	return render_template('about.html', name=name)

@app.route("/posts", methods=["GET"])
def posts(name=None): 
	#call Python Procedure - GET all projects
	cursor.callproc('getAllPosts')
	data = cursor.fetchall()
	if len(data) is not 0: 
		conn.commit()

		#make a dictionary for easy frontend templating
		dd = []
		for d in data: 
			dict = {}
			dict['date'] = d[3]
			dict['image'] = d[2]
			dict['title'] = d[1]
			dict['id'] = d[0]
			html = d[4]

			#Parse HTML to get first sentence or so for short description
			soup = bs(html, features="html.parser")
			firstParagraph = soup.p.string # first paragraph tag 
			if isinstance(firstParagraph, (str)): 
				firstParagraph[0:49] #50 characters
				dict['desc'] = firstParagraph
			else:
				dict['desc'] = ""
			dd.append(dict)

		return render_template('posts.html', name=name, data=dd)
	else:
		return json.dumps({'error':str(data[0])})

@app.route("/interests", methods=["GET"])
def interests(name=None): 
	return render_template('interests.html', name=name)	

@app.route("/post/<id>", methods=["GET"])
def getPost(id, name=None):
	#call Python Procedure - GET all projects
	cursor.callproc('getPost', id)
	data = cursor.fetchall()
	if len(data) is not 0: 
		conn.commit()

		#make a dictionary for easy frontend templating
		dd = []
		for d in data: 
			dict = {}
			dict['date'] = d[3]
			dict['image'] = "../" + d[2]
			dict['title'] = d[1]
			dict['html'] = d[4]
			dict['id'] = d[0]
			
			dd.append(dict)

		return render_template('view_post.html', name=name, data=dd)
	else:
		return json.dumps({'error':str(data[0])})

@app.route("/editPost/<id>", methods=["GET", "POST"])
def editPost(id, name=None):
	form = PostForm()

	#call Python Procedure 
	cursor.callproc('getPost', [id]) #get post from id 
	data = cursor.fetchall()

	#was the post id found? 
	if len(data) is not 0: 
		conn.commit()
		#make a dictionary for easy frontend templating
		for d in data: 
			dict = {}
			dict['date'] = d[3]
			dict['image'] = "../" + d[2]
			dict['title'] = d[1]
			dict['html'] = d[4]
			dict['switch'] = d[5]
			dict['id'] = d[0]

		#If POST -- update/alter database with new info
		if form.validate_on_submit(): 
			#title 
			title = form.title.data 

			#original date
			date = form.date.data 
			date = datetime.strptime(date, '%b %d, %Y').strftime('%Y-%m-%d')

			#main image
			if 'file' in request.files and request.files['file'].filename!="":  
				main_image = request.files['file'] 
				main_image.save(os.path.join(
					app.config['UPLOADED_IMAGES_DEST'], 
					secure_filename(main_image.filename)
				))
				main_image = app.config['UPLOADED_IMAGES_DEST'] + secure_filename(main_image.filename)
			else: 
				main_image = d[2]; 

			#is it a project - switch 
			isProject = form.isProject.data 

			#html body
			html = form.html.data 

			#parse images out of html 
			soup = bs(html, features="html.parser")
			images = soup.findAll('img')

			#upload images 
			for image in images: 
				if image['src'].find('static') == -1:
					image['src'] = upload_image(image['src'])

			#update image src changes
			html = str(soup)

			#edit blog post in database 
			try: 
				cursor.execute("UPDATE post SET title = %s, image = %s, date = %s, html = %s, isProject = %s where post.id = %s ", 
					(title, main_image, date, html, isProject, id))
				conn.commit()
			except Exception as e: 
				print("Problem inserting: " + str(e))
				return None 

			#delete previous tag entries
			cursor.callproc('deletePostTags', [id]) #get post from id 
			res = cursor.fetchall()
			print(res)

			#add as new tag entries 
			cursor.callproc('getAllTags')
			data = cursor.fetchall()
			if len(data) is not 0: 
				conn.commit()

				#make a dictionary for easy frontend templating
				dd = []
				for d in data: 
					dict = {}
					dict['name'] = d[1]
					dd.append(dict)
					
			#get tags 
			tags = []
			dict = request.form.to_dict()
			for d in data: 
				try: 
					dict[d[1]]
					tag = [d[1], d[0]]
					tags.append(tag)
				except KeyError as e: 
					#Key doesn't exist
					print("Tag key doesn't exist.")

			postid = id 
			for t in tags: 
				try: 
					cursor.execute("INSERT INTO postToTags(postid, tagid) VALUES(%s, %s)",
						(postid, t[1]))
					conn.commit()
				except Exception as e: 
					print("Problem inserting into tag/post table: " + str(e))
					return None 
		
			return redirect(url_for('posts'))
		else: 
			#get all tags associated with this post 
			cursor.callproc('getPostTags', [id])
			postTags = cursor.fetchall()

			pp = []
			for p in postTags: 
				pp.append(p[0])
			postTags = pp 
			#get all tags 
			cursor.callproc('getAllTags')
			tagNames = cursor.fetchall()
			if len(tagNames) is not 0: 
				conn.commit()

				#make a dictionary for easy frontend templating
				tt = []
				for t in tagNames: 
					dic = {}
					dic['name'] = t[1]
					tt.append(dic)

			return render_template('editPost.html', name=name, data=dict, form=form, tags=postTags, allTags=tt)
			
	else:
		return "No data"

#POST requests 
app.config['SECRET_KEY'] = 'a really long secret key'
@app.route("/post", methods=["GET", "POST"])
def post(name=None):
	form = PostForm()

	#call Python Procedure - GET all projects
	cursor.callproc('getAllTags')
	data = cursor.fetchall()
	if len(data) is not 0: 
		conn.commit()

		#make a dictionary for easy frontend templating
		dd = []
		for d in data: 
			dict = {}
			dict['name'] = d[1]
			dd.append(dict)

	if form.validate_on_submit(): 
		#title 
		title = form.title.data 

		#original date
		date = form.date.data 
		date = datetime.strptime(date, '%b %d, %Y').strftime('%Y-%m-%d')

		#main image
		if 'file' in request.files and request.files['file'].filename != "":  
			main_image = request.files['file'] 
			main_image.save(os.path.join(
				app.config['UPLOADED_IMAGES_DEST'], 
				secure_filename(main_image.filename)
			))
			main_image = app.config['UPLOADED_IMAGES_DEST'] + secure_filename(main_image.filename)
		else: 
			main_image = 'static/images/placeholder.png'

		#is it a project - switch 
		print(form.isProject)
		isProject = form.isProject.data 

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

		#get tags 
		tags = []
		dict = request.form.to_dict()
		for d in data: 
			try: 
				dict[d[1]]
				tag = [d[1], d[0]]
				tags.append(tag)
			except KeyError as e: 
				#Key doesn't exist
				print("Tag key doesn't exist.")

		#add blog post to database 
		try: 
			cursor.execute("INSERT INTO post(title, image, date, html, isProject) VALUES (%s, %s, %s, %s, %s)", 
				(title, main_image, date, html, isProject))
			conn.commit()
		except Exception as e: 
			print("Problem inserting: " + str(e))
			return None 

		#get the post id 
		postid = cursor.lastrowid 
		for t in tags: 
			try: 
				cursor.execute("INSERT INTO postToTags(postid, tagid) VALUES(%s, %s)",
					(postid, t[1]))
				conn.commit()
			except Exception as e: 
				print("Problem inserting into tag/post table: " + str(e))
				return None 

	print(form.errors)
	return render_template('postForm.html', title='Post', data=dd, form=form)


from flask import send_from_directory
import os

@app.route('/js/world-110m.json')
def worldjson():
	filename = 'world-110m.json'
	root_dir = os.path.dirname(os.getcwd())
	return send_from_directory(os.path.join(root_dir, 'static', 'js'), filename)

if __name__ == "__main__": 
	app.run()
