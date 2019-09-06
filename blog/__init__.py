from flask import (
    Flask, url_for, render_template, json, request, 
    redirect
)
from flask_login import LoginManager

login_manager = LoginManager()

import os 

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
        #uploads
        from flask_uploads import (UploadSet, 
            configure_uploads, IMAGES, TEXT, 
            DOCUMENTS, patch_request_class
        )

        images = UploadSet('images', IMAGES)
        text = UploadSet('text', TEXT)
        documents = UploadSet('documents', DOCUMENTS)
        configure_uploads(app, (images, text, documents))
        patch_request_class(app, 50 * 1024 * 1024) #50 MB max file upload

        ALLOWED_EXTENSIONS = images
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    #for handling authentication 
    login_manager.init_app(app)
    login_manager.session_protection = "strong"



    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db 
    with app.app_context():
        db.init_app(app)

        from blog import blog
        from blog import auth 

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    app.add_url_rule("/", endpoint='index')

    return app 

