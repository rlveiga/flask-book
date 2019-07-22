from flask import render_template, request, flash, redirect, url_for
from flask_wtf import Form
from flask_login import login_user, logout_user, login_required
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import Required, EqualTo
from ..models import User
from .. import db
from . import auth

class LoginForm(Form):
	username = StringField('Username:', validators=[Required()])
	password = PasswordField('Password:', validators=[Required()])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Login')

class RegistrationForm(Form):
	username = StringField('Username:', validators=[Required()])
	password = PasswordField('Password:', validators=[Required()])
	password_confirm = PasswordField('Confirm password:', validators=[Required(), EqualTo('password', message='Passwords must match.')])
	submit = SubmitField('Sign up')

	def validate_username(self, field):
		if  User.query.filter_by(username=field.data).first():
			raise ValidationError('Username is already taken')

@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()

	if form.validate_on_submit():
		if form.password.data == form.password_confirm.data:
			new_user = User(username=form.username.data, password=form.password.data)
			db.session.add(new_user)
			db.session.commit()
			login_user(new_user, True)

			return redirect(url_for('main.index'))

		else:
			flash('Passwords do not match')

	return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		existing_user = User.query.filter_by(username=form.username.data).first()

		# no user found with given username
		if existing_user is not None and existing_user.verify_password(form.password.data):
			login_user(existing_user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))

		flash('Invalid username or password')

	return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('Logged out successfully')
	return redirect(url_for('main.index'))