from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Post(db.Model):
	__tablename__ = 'posts'
	
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(64), nullable=False)
	body = db.Column(db.String(1028), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	def serialize(self):
		return {
			'id': self.id,
			'title': self.title,
			'body': self.body,
			'user_id': self.user_id
		}

	def __repr__(self):
		return '<Post %r>' % self.id

class User(UserMixin, db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True)
	password_hash = db.Column(db.String(128))
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	posts = db.relationship('Post', backref = 'post')

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def serialize(self):
		return {
			'id': self.id,
			'username': self.username,
			'role_id': self.role_id
		}

	def __repr__(self):
		return '<User %r>' % self.username

class Role(db.Model):
	__tablename__ = 'roles'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	description = db.Column(db.String(128))
	users = db.relationship('User', backref = 'role')

	def __repr__(self):
		return '<Role %r>' % self.name

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))