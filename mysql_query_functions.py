#MySQL Query Functions 
from flask import render_template
from bs4 import BeautifulSoup as bs #HTML Parsing

def getPostTags(cursor, id):
	#get all tags associated with this post 
	cursor.callproc('getPostTags', [id])
	postTags = cursor.fetchall()

	pp = []
	for p in postTags: 
		pp.append(p[0])
	return pp 

def getAllTags(cursor, conn):
	cursor.callproc('getAllTags')
	data = cursor.fetchall()
	if len(data) is not 0: 

		#make a dictionary for easy frontend templating
		dd = []
		for d in data: 
			dict = {}
			dict['id'] = d[0]
			dict['name'] = d[1]
			dd.append(dict)
	else:
		raise Exception('Could not get all tags from database.')		
	return dd

def getPostFromDB(cursor, conn, id):
	cursor.callproc('getPost', [id])
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
			dict['switch'] = d[5]
			
			dd.append(dict)
		return dd 
	else: 
		raise Exception('Could not get post: ' + id + ' from database.')			

def getAllPosts(cursor, conn): 
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
				firstParagraph = firstParagraph[0:49] #50 characters
				dict['desc'] = firstParagraph
			else:
				dict['desc'] = ""
			dd.append(dict)
	return dd  

def createTagReferences(cursor, id, request, conn):
	#get all tags 
	data = getAllTags(cursor, id)

	tags = []
	dict = request.form.to_dict()
	#Find if tag was checked or not by if it exists in the form POST
	for d in data: 
		try: 
			dict[d['name']]
			tags.append(d)
		except KeyError as e: 
			#Key doesn't exist
			print("Tag: was not selected.")

	postid = id 

	for t in tags: 
		cursor.execute("INSERT INTO postToTags(postid, tagid) VALUES(%s, %s)",
			(postid, t['id']))
		conn.commit()

def addNewTags(cursor, newTags, postid, conn):
	for t in newTags: 
		cursor.execute("INSERT INTO tags(name) VALUES(%s)",
			(t))
		conn.commit()
		tagid = cursor.lastrowid 
		#add tag reference to post id in database 
		cursor.execute("INSERT INTO postToTags(postid, tagid) VALUES(%s, %s)",
			(postid, tagid))
		conn.commit()

def editPostInDB(cursor, title, main_image, date, html, isProject, id, conn):
	cursor.execute("UPDATE post SET title = %s, image = %s, date = %s, html = %s, isProject = %s where post.id = %s ", 
		(title, main_image, date, html, isProject, id))
	conn.commit()
	