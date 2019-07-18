import os

from flask import Flask, render_template, session, redirect, url_for
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from flask_migrate import Migrate, MigrateCommand
from wtforms import StringField, SubmitField
from wtforms.validators import Required

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some long ass string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://rlveiga:@localhost/flasky'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

manager = Manager(app)
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

Bootstrap(app)

class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True)
	rep = db.Column(db.Integer)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	def __repr__(self):
		return '<User %r>' % self.username

class Role(db.Model):
	__tablename__ = 'roles'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	users = db.relationship('User', backref = 'role')

	def __repr__(self):
		return '<Role %r>' % self.name


class UserForm(Form):
	name = StringField('What is your name?', validators=[Required()])
	submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
	form = UserForm()

	if form.validate_on_submit():
		existing_user = User.query.filter_by(username=form.name.data).first()

		if existing_user is None:
			user_role = Role.query.filter_by(name='user').first()
			new_user = User(username=form.name.data, role=user_role)

			db.session.add(new_user)
			db.session.commit()
			session['known'] = False
		else:
			session['known'] = True

		session['name'] = form.name.data
		form.name.data = ''

		return redirect(url_for('user'))

	return render_template("index.html", form=form, name=session.get('name'))

@app.route('/user')
def user():
	name = session.get('name')
	known = session.get('known')

	return render_template("user.html", username=name, known=known)

@app.route('/user/<username>')
def get_user(username):
	existing_user = User.query.filter_by(username=username).first()

	if existing_user is None:
		return render_template("user.html", username=None)

	else:
		return render_template("user.html", username=existing_user.username)

if __name__ == '__main__':
	manager.run()