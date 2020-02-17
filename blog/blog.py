from flask import ( 
    Flask, url_for, render_template, json, request, redirect, Blueprint, flash, g
)
from werkzeug.exceptions import abort 
from datetime import datetime
from blog.forms import PostForm #flask forms 
from bs4 import BeautifulSoup as bs #HTML Parsing
from flask_sqlalchemy import SQLAlchemy 
from flask import current_app, g

from blog.schema import User, Post, Tag
from blog.database import get_db 
from flask_user import current_user, login_required, roles_required
from . import file_upload
from .uploadFunctions import upload_image  

bp = Blueprint("blog", __name__)

@bp.route("/", methods=["GET"])
def index(name=None): 
    posts = Post.query.all()
    for post in posts: 
      post.image = file_upload.get_file_url(post, filename="image") 
    return render_template('blog/posts.html', name=name, data=posts)

@bp.route("/post/<id>", methods=["GET"])
def getPost(id, name=None):
  try: 
      post = Post.query.get(id)
      #get all tags associated with this post 
      tags = Tag.query.filter(Tag.posts.any(id=id)).all()
      post.image = file_upload.get_file_url(post, filename="image")
      return render_template('blog/view_post.html', name=name, data=post, tags=tags)
  except Exception as e: 
      error = "Could not get post or post tags from database."
      current_app.logger.error(e) 
      return render_template('error.html', error=error)

@bp.route("/editPost/<id>", methods=["GET", "POST"])
@roles_required(['Editor'])
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
              image['style'] = "width: 100%;"

      #update image src changes
      html = str(soup)

      db = get_db() 

      #edit blog post in database 
      try: 
          post.title = title
          post.posted_date = date 
          post.revised_date = datetime.now().strftime('%Y-%m-%d')
          post.html = html 
          post.is_project = isProject
          #main image
          if 'file' in request.files and request.files['file'].filename!="":  
            main_image = request.files['file'] 
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
          current_app.logger.info("Tag was not selected.")
          current_app.logger.info(e)

      #get the newly created tags 
      newTags = request.form.getlist('newTag[]')
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
      return redirect(url_for('index'))
  else: 
      #get all tags associated with this post 
      postTags = []
      for t in post.tags: 
        postTags.append(t.name)
      #get all tags
      allTags = Tag.query.all()
      post.image = file_upload.get_file_url(post, filename="image")
      return render_template('blog/editPost.html', name=name, data=post, form=form, tags=postTags, allTags=allTags)

#POST requests 
@bp.route("/post", methods=["GET", "POST"])
@roles_required(['Editor'])
def post(name=None):
    form = PostForm()

    allTags = Tag.query.all() 

    if form.validate_on_submit(): 
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
            post = Post(title=title, html=html, posted_date=date, revised_date=None, 
                is_project=isProject, author=author_id, tags=tagIds )

            #main image
            if 'file' in request.files and request.files['file'].filename != "":  
                main_image = request.files['file'] 
                post = file_upload.save_files(post, files={
                  "image": main_image
                })
            else: 
                main_image = 'static/images/placeholder.png'
                
            db.session.add(post)
            db.session.commit()
        except Exception as e: 
            current_app.logger.error("Problem inserting/creating post into DB: " + str(e))
            return render_template('error.html', error="Could not create post.") 

    current_app.logger.error(form.errors)
    return render_template('blog/postForm.html', title='Post', data=allTags, form=form)

