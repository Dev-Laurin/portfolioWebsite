from flask import ( 
    Flask, url_for, render_template, json, request, redirect, 
    Blueprint, flash, g, current_app
)
#HTML Parsing
from bs4 import BeautifulSoup as bs 

#Database
from blog.schema import Post, Tag

#Upload files
from blog import file_upload
from .uploadFunctions import upload_image  

from datetime import date, datetime

def deleteAllTags(post, db):
  #delete all tag-post relationships with this post 
  post.tags = []
  db.session.add(post)
  db.session.commit()

def updateTags(post, db, form, tags):
  formDict = form.to_dict() #request.form.to_dict()
  #Find if tag was checked or not by if it exists in the form POST
  for t in tags: 
    try: 
      formDict[t.name]
      tag = Tag.query.filter_by(name=t.name).first()
      tag.posts.append(post)
      db.session.add(tag)
      db.session.commit()
    except KeyError as e: 
      #Key doesn't exist
      current_app.logger.info("Tag was not selected.")
      current_app.logger.info(e)

def addTags(post, db, form, tags):
  for t in tags: 
    #see if tag is already created 
    tag = Tag.query.filter_by(name=t).first()
    if tag is not None:
        #tag already exists, update relationship
        try: 
          tag.posts.append(post)
          db.session.add(tag)
          db.session.commit()
        except Exception as e: 
          current_app.logger.error("Problem updating tags.")
          current_app.logger.error(e)
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
          current_app.logger.error("Problem creating new tags.")
          current_app.logger.error(e)
          error = "Error occurred."
          return render_template('error.html', error=error)
  return redirect(url_for('getAllPosts'))

def updatePostTags(post, db, form, tags):
  deleteAllTags(post, db)
  #Add the old tabs that were kept
  updateTags(post, db, form, Tag.query.all())
  #Add the new tabs
  addTags(post, db, form, tags)

def updatePost(form, post, db, tags, files):
  #title 
  title = form.title.data 

  #original date
  date = form.date.data 
  date = datetime.strptime(date, '%b %d, %Y').strftime('%Y-%m-%d')

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
          image['class'] = "center"
          image['onError'] = "this.onerror=null;this.src='/static/vw_image_placeholder.png';this.width='150';this.height='150';"

  #update image src changes
  html = str(soup) 

  #edit blog post in database 
  try: 
      post.title = title
      post.posted_date = date 
      post.revised_date = datetime.now().strftime('%Y-%m-%d')
      post.html = html 
      post.is_project = isProject
      #main image
      if 'file' in files and files['file'].filename!="":  
        main_image = files['file'] 
        post = file_upload.save_files(post, files={
        "image": main_image
        })
      db.session.add(post)
      db.session.commit()
  except Exception as e: 
      current_app.logger.error("Problem updating post.")
      current_app.logger.error(e)
      error = "Error occurred."
      return render_template('error.html', error=error)

  # Update the tags 
  updatePostTags(post, db, form, tags)