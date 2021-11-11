from flask import ( 
    Flask, url_for, render_template, json, request, redirect, 
    Blueprint, flash, g, current_app
)
from werkzeug.exceptions import abort 

#Forms
from blog.forms import PostForm #flask forms 

#Database
from flask_sqlalchemy import SQLAlchemy 
from blog.schema import User, Post, Tag
from blog.database import get_db 

#Flask User - Auth
from flask_user import current_user, login_required, roles_required

#Upload files
from blog import file_upload
from blog.uploadFunctions import upload_image, create_thumbnail

#Update posts in database 
from blog.updatePost import updatePost

#Other
from datetime import date, datetime


bp = Blueprint("blog", __name__)
current_year = date.today().year

@bp.route("/", methods=["GET"])
def getAllPosts(name=None): 
    posts = Post.query.all()
    for post in posts: 
      post.image = file_upload.get_file_url(post, filename="image") 
      post.mobile_image = file_upload.get_file_url(post, filename="mobile_image") 
    return render_template('blog/posts.html', name=name, data=posts, current_year=current_year)

@bp.route("/post/<id>", methods=["GET"])
def getPost(id, name=None):
    try: 
        post = Post.query.get(id)
        #get all tags associated with this post 
        tags = Tag.query.filter(Tag.posts.any(id=id)).all()
        post.image = file_upload.get_file_url(post, filename="image")
        post.mobile_image = file_upload.get_file_url(post, filename="mobile_image")
        return render_template('blog/view_post.html', name=name, data=post, tags=tags, current_year=current_year)
    except Exception as e: 
        error = "Could not get post or post tags from database."
        current_app.logger.error(e) 
        return render_template('error.html', error=error)

@bp.route("/post/<id>", methods=["GET", "POST"])
@roles_required(['Editor'])
def editPost(id, name=None):
    form = PostForm()

    #Does post exist? 
    post = Post.query.get_or_404(id)

    # update/alter database with new info
    if form.validate_on_submit(): 

        newTags = request.form.getlist('newTag[]')
        updatePost(form, post, get_db(), newTags, request.files)
        
    else: 
        #get all tags associated with this post 
        postTags = []
        for t in post.tags: 
            postTags.append(t.name)
            #get all tags
            allTags = Tag.query.all()
            post.image = file_upload.get_file_url(post, filename="image")
            post.mobile_image = file_upload.get_file_url(post, filename="mobile_image")
            return render_template('blog/editPost.html', name=name, data=post, form=form, tags=postTags, allTags=allTags, current_year=current_year)

#POST requests 
@bp.route("/post", methods=["POST"])
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
            image['class'] = "center"
            image['onError'] = "this.onerror=null;this.src='/static/vw_image_placeholder.png';this.width='150';this.height='150';"
            #Create thumbnail
            image['thumbnail'] = create_thumbnail(src=image['src'])

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
                #Create thumbnail for mobile
                create_thumbnail(infile=main_image)
            else: 
                main_image = 'static/images/placeholder.png'
                
            db.session.add(post)
            db.session.commit()
        except Exception as e: 
            current_app.logger.error("Problem inserting/creating post into DB: " + str(e))
            return render_template('error.html', error="Could not create post.") 

    current_app.logger.error(form.errors)
    return render_template('blog/postForm.html', title='Post', data=allTags, form=form, current_year=current_year)

#Delete Post
@bp.route("/deletePost/<id>", methods=["POST"])
@roles_required(['Editor'])
def deletePost(id, name=None):
    try: 
        db = get_db()
        post = Post.query.get(id)
        db.session.delete(post)
        db.session.commit()
        return redirect('/')
    except Exception as e: 
        error = "Could not delete post."
        current_app.logger.error(e) 
        return render_template('error.html', error=error)