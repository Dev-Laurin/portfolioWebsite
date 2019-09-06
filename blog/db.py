from flask_sqlalchemy import SQLAlchemy
import click  
from flask import current_app, g
from flask.cli import with_appcontext

def get_db(): 
	if 'db' not in g:
		g.db = SQLAlchemy(current_app)
	return g.db 

def close_db(e=None):
	db = g.pop('db', None)

	if db is not None: 
		db.session.close()

def init_db():
	db = get_db()
	import blog.schema 
	db.create_all()
	db.session.commit()

def init_app(app):
	app.teardown_appcontext(close_db)
	init_db()