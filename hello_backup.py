#flash is for messages
from flask import Flask, render_template, flash, request,redirect,url_for

#for doing forms
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo,Length

# for database
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

# for migrating database
from flask_migrate import Migrate

# for hashing
from werkzeug.security import generate_password_hash, check_password_hash

#inporting textarea which are bigger than regular text fields
from wtforms.widgets import TextArea

#login
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user







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





#login stuff - they initiate the login process
login_manager = LoginManager()
login_manager.init_app(app)
#here we tell that login route is the login page
login_manager.login_view = 'login'
# to load the user when we login
@login_manager.user_loader
def load_user(user_id):
	# we are telling them to use user from here
	return Userss.query.get(int(user_id))








#create dbms model(kinda like table, but not table)
#UserMixin is for login logout stuff
class Userss(db.Model,UserMixin):
	#to take this shit from mysql instead of putting it all here we can just use this inside the model class
	#|	__table__ = db.Table('users', db.metadata, autoload_with=db.engine)
	id=db.Column(db.Integer,primary_key=True)
	username=db.Column(db.String(20),nullable=False,unique=True)
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
#create all will not update pre existing model, only create new one
#thats why we need to use migrate


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
	username = StringField("Username", validators=[DataRequired()])
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

#login form
class LoginForm(FlaskForm):
	username=StringField("Username",validators=[DataRequired()])
	password=PasswordField("Password",validators=[DataRequired()])
	submit=SubmitField("Submit")







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
		user = Userss.query.filter_by(email=form.email.data).first()
		if user is None:
			#hashing password bfr storing
			hashed_pw=generate_password_hash(form.password_hash.data)
			user = Userss(name=form.name.data,username=form.username.data,email=form.email.data,favorite_color=form.favorite_color.data,password_hash=hashed_pw)
			db.session.add(user)
			db.session.commit()
			flash("User added successfully")
		else:
			flash("Another user already registered in this email")
		name = form.name.data
		form.name.data=''
		form.username.data=''
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
		name_to_update.username = request.form['username']
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
@login_required
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
#@login_required
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
@login_required
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
@login_required
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

#login page
@app.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Userss.query.filter_by(username=form.username.data).first()
		if user:
			#we check the hash
			if check_password_hash(user.password_hash,form.password.data):
				login_user(user)
				flash("Login successful")
				return redirect(url_for('dashboard'))
			else:
				flash("Wrong password... Try again...")
		else:
			flash("User doesn't exist... try again...")
	return render_template('login.html',form=form)

#for loggin out
@app.route('/logout')
@login_required
#login required means u can't access this route unless u r logged in
#there is another way too
def logout():
	logout_user()
	flash("You have been logged out")
	return redirect(url_for('login'))


#dashboard page
@app.route('/dashboard')
@login_required
def dashboard():
	form=UserForm();
	name_to_update = Userss.query.get_or_404(current_user.id)
	if request.method=='POST':
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favorite_color = request.form['favorite_color']
		name_to_update.username = request.form['username']
		try:
			db.session.commit()
			flash("Updated successfully")
			return render_template('dashboard.html',form,name_to_update=name_to_update)
		except:
			flash("Error.. try again..")
			return render_template('dashboard.html',form=form,name_to_update=name_to_update)
	else:
		return render_template('dashboard.html',form=form,name_to_update=name_to_update)
	return render_template('dashboard.html')






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

