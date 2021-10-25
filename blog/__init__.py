from flask import (
    Flask, url_for, render_template, json, request, 
    redirect
)
from flask_file_upload.file_upload import FileUpload 
from flask_user import UserManager, roles_required, current_user
import os 
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
file_upload = FileUpload(db=db)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import database 
    with app.app_context():
        db.init_app(app)
        file_upload.init_app(app, db) 
        
        from blog import blog
        from .schema import User
         #uploads
          
        user_manager = UserManager(app, db, User)

        #uploads
        from flask_uploads import (UploadSet, 
            configure_uploads, IMAGES, 
            DOCUMENTS
        )

        images = UploadSet('images', IMAGES)
        documents = UploadSet('documents', DOCUMENTS)
        configure_uploads(app, (images, documents))

        ALLOWED_EXTENSIONS = images
      #  dev_db(user_manager)

    app.register_blueprint(blog.bp)

    app.add_url_rule("/", endpoint='index')

    return app 

def dev_db(user_manager):
    from .schema import Role, User 
    db.drop_all()
    db.create_all()

    #Roles 
    editor = Role(name='Editor')
    #users
    user = User(username="laurin", 
        password=user_manager.hash_password("herewegotesting44"))
    user.roles.append(editor)
    db.session.add(user)
    db.session.commit()

