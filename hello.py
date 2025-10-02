from flask import Flask, render_template

#creating flask instance
app = Flask(__name__)

#creating route decorator
@app.route('/')

def index():
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
