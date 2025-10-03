#flash is for messages
from flask import Flask, render_template, flash

#for doing forms
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# for database
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#creating flask instance
app = Flask(__name__)
#secret key
app.config['SECRET_KEY'] = "my super secret key"
#setting database uri
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///userss.db'
#initialise db
db = SQLAlchemy(app)

#create dbms model
class Userss(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(50),nullable=False)
	email=db.Column(db.String(50),nullable=False,unique=True)
	date_added=db.Column(db.DateTime,default=datetime.utcnow)

	def __repr__(self):
		return '<Name %r>' %self.name

#create a form class
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	submit = SubmitField("Submit")

#create a form class
class NamerForm(FlaskForm):
	name = StringField("whats ur name?", validators=[DataRequired()])
	#theres a lot of validators we could use to control the input of forms in flask_wtf
	submit = SubmitField("Submit")

#creating route decorator
@app.route('/')

def index():
	flash("Welcome to ma casa!!")
	return render_template("index.html")
	#flask will find it in templates directory

@app.route('/user/<name>')

def user(name):
	#the name entered in url will be passed as paramter
	#then we can use formatting to get it in the return string
	#return "<h1>Hello {}!!</h1>".format(name)
	l=['reggie','jc','tupac','biggie',33]
	return render_template("user.html",name=name,l=l)
	#the first part is used in html page using {{}}, its convention to use same variable name but not necessary
	#we can pass any variable like this

# custom error handler

#flask has some mechanism to deal with it instead of routes

#invlaid url
@app.errorhandler(404)
def not_found(e):
	return render_template("404.html"),404

#internal server error
@app.errorhandler(500)
def not_found(e):
	return render_template("500.html"),500

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

@app.route('/user/add',methods=['GET','POST'])
def adduser():
	name=None
	form = UserForm()
	if form.validate_on_submit():
		user = Userss.query.filter_by(email=form.email.data).first()
		if user is None:
			user = Userss(name=form.name.data,email=form.email.data)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data=''
		form.email.data=''
		flash("User added successfully")
	our_users=Userss.query.order_by(Userss.date_added)
	return render_template('adduser.html',form=form,name=name,our_users=our_users)