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
from flask import current_app, g

from blog.auth import login_required
from blog.schema import User, Post, Tag
from blog.database import get_db 

bp = Blueprint("blog", __name__)

@bp.route("/", methods=["GET"])
def index(name=None): 
    posts = Post.query.all()
    return render_template('blog/posts.html', name=name, data=posts)

@bp.route("/post/<id>", methods=["GET"])
def getPost(id, name=None):
  try: 
      post = Post.query.get(id)
      #get all tags associated with this post 
      tags = Tag.query.filter(Tag.posts.any(id=id)).all()
      return render_template('blog/view_post.html', name=name, data=post, tags=tags)
  except Exception as e: 
      error = "Could not get post or post tags from database."
      print(e) 
      return render_template('error.html', error=error)

@login_required
@bp.route("/editPost/<id>", methods=["GET", "POST"])
def editPost(id, name=None):
  form = PostForm()

  #Does post exist? 
  post = Post.query.get_or_404(id)

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
              current_app.config['UPLOADED_IMAGES_DEST'], 
              secure_filename(main_image.filename)
          ))
          main_image = current_app.config['UPLOADED_IMAGES_DEST'] + secure_filename(main_image.filename)
      else: 
          main_image = post.image; 

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

      db = get_db() 

      #edit blog post in database 
      try: 
          post.title = title
          post.image = main_image
          post.posted_date = date 
          post.revised_date = datetime.now().strftime('%Y-%m-%d')
          post.html = html 
          post.is_project = isProject
          db.session.add(post)
          db.session.commit()
      except Exception as e: 
          print("Problem updating post.")
          print(e)
          error = "Error occurred."
          return render_template('error.html', error=error)

      #delete all tag-post relationships with this post 
      post.tags = []
      db.session.add(post)
      db.session.commit()

      #add old tag relationships to post
      data = Tag.query.all()
      dict = request.form.to_dict()
      #Find if tag was checked or not by if it exists in the form POST
      for d in data: 
        try: 
          dict[d.name]
          tag = Tag.query.filter_by(name=d.name).first()
          tag.posts.append(post)
          db.session.add(tag)
          db.session.commit()
        except KeyError as e: 
          #Key doesn't exist
          print("Tag: was not selected.")

      #get the newly created tags 
      newTags = request.form.getlist('newTag[]')
      print(newTags)
      for t in newTags: 
          #see if tag is already created 
          tag = Tag.query.filter_by(name=t).first()
          if tag is not None:
              #tag already exists, update relationship
              try: 
                tag.posts.append(post)
                db.session.add(tag)
                db.session.commit()
              except Exception as e: 
                print("Problem updating tags.")
                print(e)
                error = "Error occurred."
                return render_template('error.html', error=error)
          else: 
              #create the tag and add the relationship
              try: 
                tag = Tag(name=t)
                tag.posts.append(post)
                db.session.add(tag)
                db.session.commit()
              except Exception as e: 
                print("Problem creating new tags.")
                print(e)
                error = "Error occurred."
                return render_template('error.html', error=error)
      return redirect(url_for('index'))
  else: 
      #get all tags associated with this post 
      postTags = []
      for t in post.tags: 
        postTags.append(t.name)
      #get all tags
      allTags = Tag.query.all()
      return render_template('blog/editPost.html', name=name, data=post, form=form, tags=postTags, allTags=allTags)

#POST requests 
@login_required
@bp.route("/post", methods=["GET", "POST"])
def post(name=None):
    form = PostForm()

    allTags = Tag.query.all() 

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
              current_app.config['UPLOADED_IMAGES_DEST'], 
              secure_filename(main_image.filename)
            ))
            main_image = current_app.config['UPLOADED_IMAGES_DEST'] + secure_filename(main_image.filename)
        else: 
            main_image = 'static/images/placeholder.png'

        #is it a project - switch 
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

        #get the newly created tags 
        newTags = request.form.getlist('newTag[]')

        #add the new tags to the database 
        tagIds = []
        db = get_db() 
        for t in newTags: 
            tag = Tag(t)
            db.session.add(tag)
            db.session.commit()
            tagIds.push(tag.id)

        author_id = 1 
        #add blog post to database 
        try: 
            post = Post(title=title, html=html, image=main_image, posted_date=date, revised_date=None, 
                is_project=isProject, author=author_id, tags=tagIds )
            db.session.add(post)
            db.session.commit()
        except Exception as e: 
            print("Problem inserting/creating post into DB: " + str(e))
            return render_template('error.html', error="Could not create post.") 

    print(form.errors)
    return render_template('blog/postForm.html', title='Post', data=allTags, form=form)

