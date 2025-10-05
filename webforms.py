#for doing forms
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo,Length


#inporting textarea which are bigger than regular text fields
from wtforms.widgets import TextArea


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
