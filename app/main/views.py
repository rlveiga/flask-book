from flask import render_template, session, redirect, url_for, jsonify
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required
from . import main
from .. import db
from ..models import User, Role

class UserForm(Form):
	username = StringField('Username:', validators=[Required()])
	# password = PasswordField('Password:', validators=[Required()])
	submit = SubmitField('Submit')

@main.route('/', methods=['GET', 'POST'])
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

		return redirect(url_for('.user'))

	return render_template("index.html", form=form, name=session.get('name'))

@main.route('/user')
def user():
	name = session.get('name')
	known = session.get('known')

	return render_template("user.html", username=name, known=known)

@main.route('/user/<username>')
def get_user(username):
	existing_user = User.query.filter_by(username=username).first()

	if existing_user is None:
		return render_template("user.html", username=None)

	else:
		return render_template("user.html", username=existing_user.username)