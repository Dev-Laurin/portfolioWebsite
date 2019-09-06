from flask import ( 
    Flask, url_for, render_template, json, request, redirect, Blueprint, flash, g
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort 
from datetime import datetime
from blog.forms import PostForm #flask forms 
from bs4 import BeautifulSoup as bs #HTML Parsing
import uuid #Filename random generator
import base64 #base64 image decoding 
import re #substring search 
import os 
from flask_sqlalchemy import SQLAlchemy 

from blog.auth import login_required
from blog.schema import User, Post, Tag

bp = Blueprint("blog", __name__)

@bp.route("/", methods=["GET"])
def index(name=None): 
    posts = Post.query.all() 
    return render_template('blog/posts.html', name=name, data=posts)

# @bp.route("/post/<id>", methods=["GET"])
# def getPost(id, name=None):
#   try: 
#       post = getPostFromDB(cursor, conn, id)
#       #get all tags associated with this post 
#       tags = getPostTags(cursor, id)
#       return render_template('blog/view_post.html', name=name, data=post, tags=tags)
#   except Exception as e: 
#       error = "Could not get post or post tags from database."
#       print(e) 
#       return render_template('error.html', error=error)

# @login_required
# @bp.route("/editPost/<id>", methods=["GET", "POST"])
# def editPost(id, name=None):
#   form = PostForm()

#   #Does post exist? 
#   try: 
#       post = getPostFromDB(cursor, conn, id)
#       post = post[0]

#       #If POST -- update/alter database with new info
#       if form.validate_on_submit(): 
#           #title 
#           title = form.title.data 

#           #original date
#           date = form.date.data 
#           date = datetime.strptime(date, '%b %d, %Y').strftime('%Y-%m-%d')

#           #main image
#           if 'file' in request.files and request.files['file'].filename!="":  
#               main_image = request.files['file'] 
#               main_image.save(os.path.join(
#                   app.config['UPLOADED_IMAGES_DEST'], 
#                   secure_filename(main_image.filename)
#               ))
#               main_image = app.config['UPLOADED_IMAGES_DEST'] + secure_filename(main_image.filename)
#           else: 
#               main_image = d[2]; 

#           #is it a project - switch 
#           isProject = form.isProject.data 

#           #html body
#           html = form.html.data 

#           #parse images out of html 
#           soup = bs(html, features="html.parser")
#           images = soup.findAll('img')

#           #upload images 
#           for image in images: 
#               if image['src'].find('static') == -1:
#                   image['src'] = upload_image(image['src'])

#           #update image src changes
#           html = str(soup)

#           #edit blog post in database 
#           try: 
#               editPostInDB(cursor, title, main_image, date, html, isProject, id, conn)
#           except Exception as e: 
#               print("Problem updating post." + e)
#               error = "Error occurred."
#               return render_template('error.html', error=error)

#           #delete previous tag entries
#           try: 
#               cursor.callproc('deletePostTags', [id]) #get post from id 
#           except Exception as e: 
#               error = "Error occurred."
#               print("Exception thrown while deleting post-tag reference. PostID: " + id + e)
#               return render_template('error.html', error=error)

#           #add as new tag entries
#           try:  
#               createTagReferences(cursor, id, request, conn)
#           except Exception as e: 
#               print("Problem inserting into tag/post table: " + str(e))
#               error = "Error occurred."
#               return render_template('error.html', error=error)

#           #get the newly created tags 
#           newTags = request.form.getlist('newTag[]')
#           #add new tags to database 
#           try: 
#               addNewTags(cursor, newTags, id, conn)
#           except Exception as e: 
#               print("Problem creating new tags." + e)
#               error = "Error occurred."
#               return render_template('error.html', error=error)
            
#           return redirect(url_for('posts'))
#       else: 
#           #get all tags associated with this post 
#           postTags = getPostTags(cursor, id)
#           #get all tags
#           allTags = getAllTags(cursor, conn)
#           return render_template('blog/editPost.html', name=name, data=post, form=form, tags=postTags, allTags=allTags)
#   except Exception as e:
#       print(e)
#       error = "Error occurred. Post doesn't exist."
#       return render_template('error.html', error=error)

# #POST requests 
# @login_required
# @bp.route("/post", methods=["GET", "POST"])
# def post(name=None):
#   form = PostForm()

#   allTags = getAllTags(cursor, conn)

#   if form.validate_on_submit(): 
#       #title 
#       title = form.title.data 

#       #original date
#       date = form.date.data 
#       date = datetime.strptime(date, '%b %d, %Y').strftime('%Y-%m-%d')

#       #main image
#       if 'file' in request.files and request.files['file'].filename != "":  
#           main_image = request.files['file'] 
#           main_image.save(os.path.join(
#               app.config['UPLOADED_IMAGES_DEST'], 
#               secure_filename(main_image.filename)
#           ))
#           main_image = app.config['UPLOADED_IMAGES_DEST'] + secure_filename(main_image.filename)
#       else: 
#           main_image = 'static/images/placeholder.png'

#       #is it a project - switch 
#       isProject = form.isProject.data 

#       #html body
#       html = form.html.data 

#       #parse images out of html 
#       soup = bs(html, features="html.parser")
#       images = soup.findAll('img')

#       #upload images 
#       for image in images: 
#           image['src'] = upload_image(image['src'])

#       #update image src changes
#       html = str(soup)

#       #add blog post to database 
#       try: 
#           cursor.execute("INSERT INTO post(title, image, date, html, isProject) VALUES (%s, %s, %s, %s, %s)", 
#               (title, main_image, date, html, isProject))
#           conn.commit()
#       except Exception as e: 
#           print("Problem inserting: " + str(e))
#           return None 

#       #get the post id 
#       postid = cursor.lastrowid 
#       createTagReferences(cursor, postid, request, conn)

#   print(form.errors)
#   return render_template('postForm.html', title='Post', data=allTags, form=form)

