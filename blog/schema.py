from werkzeug.security import generate_password_hash, check_password_hash
from blog.database import get_db
from datetime import datetime 

db = get_db()

#Many to Many 
tags = db.Table('tags',
	db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
	db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
) 

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	html = db.Column(db.Text, nullable=False)
	image = db.Column(db.String(200))
	posted_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	revised_date = db.Column(db.DateTime)
	is_project = db.Column(db.Integer)
	author = db.Column(db.Integer, db.ForeignKey('user.id'),
		nullable=False)
	tags = db.relationship('Tag', secondary=tags, lazy='subquery',
		backref=db.backref('posts', lazy=True))

	def __repr__(self):
		return '<Post %r>' % self.title 

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<User %r' % self.username 

class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False)

	def __repr__(self):
		return '<Tag %r' % self.name 


