from flask import render_template, session, redirect, url_for, jsonify
from flask_wtf import Form
from flask_login import login_required, current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Required
from . import main
from .. import db
from ..models import User, Role, Post

class UserForm(Form):
	username = StringField('Username:', validators=[Required()])
	password = PasswordField('Password:', validators=[Required()])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Submit')

class NewPostForm(Form):
	title = StringField('Post title:', validators=[Required()])
	body = StringField('Post body:', validators=[Required()])
	submit = SubmitField('Submit post')

@main.route('/', methods=['GET', 'POST'])
def index():
	posts = Post.query.order_by(Post.id.desc()).all()
	posts_obj = []

	for post in posts:
		user = User.query.filter_by(id=post.user_id).first()
		posts_obj.append({'post': post, 'user': user})

	return render_template("index.html", posts=posts_obj)

@main.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
	form = NewPostForm()

	if form.validate_on_submit():
		new_post = Post(title=form.title.data, body=form.body.data, user_id=current_user.id)
		db.session.add(new_post)
		db.session.commit()

		return redirect(url_for('main.index'))

	return render_template("new_post.html", form=form)

@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first()

	if user is None:
		response = {
			'error': 'User not found'
		}
		return jsonify(response)

	posts = user.posts

	return render_template("profile.html", user=user, posts=posts)