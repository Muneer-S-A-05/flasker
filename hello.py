#flash is for messages
from flask import Flask, render_template, flash, request,redirect,url_for

#for doing forms
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo,Length

# for database
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# for migrating database
from flask_migrate import Migrate

# for hashing
from werkzeug.security import generate_password_hash, check_password_hash

#get current date
from datetime import date

#inporting textarea which are bigger than regular text fields
from wtforms.widgets import TextArea




#creating flask instance
app = Flask(__name__)

#secret key
app.config['SECRET_KEY'] = "my super secret key"



#setting database uri for sqlite
#app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///userss.db'

#setting database uri for mysql, our_users is db name
# we need to make a database first
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:1234@localhost/sample'

#initialise db
db = SQLAlchemy(app)
#telling it to migrate app with db
migrate = Migrate(app,db)
#we then need to setup the migration stuff with
#|	flask db init
#this will create migrations folder with various versions
#then we can migrate and commit using
#|	flask db migrate -m 'Initial migration or other message'
#|	flask db upgrade




#create dbms model
class Userss(db.Model):
	#to take this shit from mysql instead of putting it all here we can just use this inside the model class
	#|	__table__ = db.Table('users', db.metadata, autoload_with=db.engine)
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(50),nullable=False)
	email=db.Column(db.String(50),nullable=False,unique=True)
	favorite_color=db.Column(db.String(20))
	date_added=db.Column(db.DateTime,default=datetime.utcnow)
	#password
	password_hash = db.Column(db.String(256))
	#some properties for password
	@property
	def password(self):
		raise AttributeError('password is not readable attribue!')
	@password.setter
	def password(self,password):
		self.password_hash=generate_password_hash(password)
	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)

	# repr part is how our model will be presented when we print it
	def __repr__(self):
		return '<Name %r>' %self.name
#after making this, we need to go to terminal and get the model created.
#we run this in python in terminal for that
#|	from hello import app,db
#|	with app.app_context:
#|		db.create_all()


#blog post needs a model
class Posts(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String(100))
	#we use text we want lot of space
	content = db.Column(db.Text)
	author = db.Column(db.String(100))
	date_posted = db.Column(db.DateTime,default=datetime.utcnow)
	slug=db.Column(db.String(100))





#create a form class for adduser
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	favorite_color = StringField("Favorite Color")
	password_hash=PasswordField('Password',validators=[DataRequired(),EqualTo('password_hash2',message='Passwords must match')])
	password_hash2=PasswordField('Confirm Password',validators=[DataRequired()])
	submit = SubmitField("Submit")

#create a form class for name
class NamerForm(FlaskForm):
	name = StringField("whats ur name?", validators=[DataRequired()])
	#theres a lot of validators we could use to control the input of forms in flask_wtf
	submit = SubmitField("Submit")

# form for handling password
class PasswordForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired()])
	password_hash = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

# form to handle posts
class PostForm(FlaskForm):
	title = StringField("Title",validators=[DataRequired()])
	content = StringField("Content",validators=[DataRequired()],widget=TextArea())
	author = StringField("Author",validators=[DataRequired()])
	slug = StringField("Slug",validators=[DataRequired()])
	submit = SubmitField("Submit")



#creating route decorator
@app.route('/')
def index():
	return render_template("index.html")
	#flask will find it in templates directory

#page that just prints url name
@app.route('/user/<name>')
def user(name):
	#the name entered in url will be passed as paramter
	#then we can use formatting to get it in the return string
	#return "<h1>Hello {}!!</h1>".format(name)
	l=['reggie','jc','tupac','biggie',33]
	return render_template("user.html",name=name,l=l)
	#the first part is used in html page using {{}}, its convention to use same variable name but not necessary
	#we can pass any variable like this

#name page
@app.route('/name',methods=['GET','POST'])
def name():
	name=None
	form=NamerForm()
	#validate form
	if form.validate_on_submit():
		name=form.name.data
		form.name.data=''
		#message to flash, we dont need to pass it in return
		flash("Form submitted successfully")
	return render_template('name.html',name=name,form=form)

#page to add user to list
@app.route('/user/add',methods=['GET','POST'])
def adduser():
	name=None
	form = UserForm()
	if form.validate_on_submit():
		hashed_pw=generate_password_hash(form.password_hash.data)
		user = Userss.query.filter_by(email=form.email.data).first()
		if user is None:
			print(hashed_pw)
			user = Userss(name=form.name.data,email=form.email.data,favorite_color=form.favorite_color.data,password_hash=hashed_pw)
			db.session.add(user)
			db.session.commit()
			flash("User added successfully")
		else:
			flash("Another user already registered in this email")
		name = form.name.data
		form.name.data=''
		form.email.data=''
		form.favorite_color.data=''
		form.password_hash.data=''
	our_users=Userss.query.order_by(Userss.date_added)
	return render_template('adduser.html',form=form,name=name,our_users=our_users)

#page to update user details
@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
	form=UserForm();
	name_to_update = Userss.query.get_or_404(id)
	if request.method=='POST':
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favorite_color = request.form['favorite_color']
		try:
			db.session.commit()
			flash("Updated successfully")
			return render_template('update.html',name_to_update=name_to_update,form=form,id=id)
		except:
			flash("Error.. try again..")
			return render_template('update.html',form=form,name_to_update=name_to_update)
	else:
		return render_template('update.html',form=form,id=id, name_to_update=name_to_update)

#page to delete user from id
@app.route('/delete/<int:id>')
def delete(id):
	user_delete = Userss.query.get_or_404(id)
	name=None
	form=UserForm()
	our_users=Userss.query.order_by(Userss.date_added)
	try:
		name=user_delete.name
		db.session.delete(user_delete)
		db.session.commit()
		flash("Deleted successfully")
		return render_template('adduser.html',form=form,name=name,our_users=our_users)
	except:
		flash("Oops! There was an error...")
		return render_template('adduser.html',form=form,name=name,our_users=our_users)

#test page for checking password
@app.route('/testpw',methods=['GET','POST'])
def testpw():
	email=None
	password=None
	pw_to_check=None
	passed=None
	form=PasswordForm()

	#validate form
	if form.validate_on_submit():
		email=form.email.data
		password=form.password_hash.data
		form.email.data=''
		form.password_hash.data=''

		#getting user info
		pw_to_check = Userss.query.filter_by(email=email).first()

		#checking password
		passed=check_password_hash(pw_to_check.password_hash,password)

	return render_template('testpw.html',email=email,password=password,form=form,pw_to_check=pw_to_check,passed=passed)

# return json
@app.route('/date')
def get_current_date():
	#any python dictionary will be treated as json on return
	favorite_pizza = {"tom":"peproni","jack":"cheese"}
	return favorite_pizza

# to add blog posts
@app.route('/add_post',methods=['GET','POST'])
def add_post():
	form = PostForm()
	if form.validate_on_submit():
		post=Posts(title=form.title.data,content=form.content.data,author=form.author.data,slug=form.slug.data)
		form.title.data=''
		form.content.data=''
		form.author.data=''
		form.slug.data=''
		db.session.add(post)
		db.session.commit()
		flash("Blog post submitted succeessfully")
	return render_template("add_post.html",form=form)

#to see all blogs
@app.route('/posts')
def posts():
	posts=Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html",posts=posts)

#to see individual posts
@app.route('/posts/<int:id>')
def post(id):
	post=Posts.query.get_or_404(id)
	return render_template('post.html',post=post)

#edit posts
@app.route('/posts/edit/<int:id>',methods=['GET','POST'])
def edit_posts(id):
	post = Posts.query.get_or_404(id)
	form=PostForm()
	if form.validate_on_submit():
		post.title=form.title.data
		post.author=form.author.data
		post.slug=form.slug.data
		post.content=form.content.data
		db.session.add(post)
		db.session.commit()
		flash('BLog updated successfully')
		return redirect(url_for('post',id=id))
	form.title.data=post.title
	form.author.data=post.author
	form.slug.data=post.slug
	form.content.data=post.content
	return render_template('edit_post.html',form=form)

#edit posts
@app.route('/posts/delete/<int:id>')
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	try:
		db.session.delete(post_to_delete)
		db.session.commit()
		flash("Post deleted!")
		return redirect(url_for('posts'))
	except:
		flash('Oops, couldnt delete post')
		return redirect(url_for('posts'))





# custom error handler
#flask has some mechanism to deal with it instead of routes
#invlaid url
@app.errorhandler(404)
def not_found(e):
	return render_template("404.html"),404

#internal server error
@app.errorhandler(500)
def internal_error(e):
	return render_template("500.html"),500

# to call a trigger on purpose, make sure debugger is off
#
#@app.route('/trigger-500')
#def trigger_500():
#	raise Exception("This is a test 500 error")

