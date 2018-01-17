from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
	username = StringField("Username", validators=[ DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField("Enter a Username", validators =[DataRequired()])
	email_addr = StringField("Enter your email address", validators=[DataRequired(), Email()])
	password_fi = PasswordField("Set your password", validators = [DataRequired()])
	password2 = PasswordField("Re-enter password", validators= [DataRequired(), EqualTo("password_fi")])
	submit = SubmitField("Register !!!")

	def validate_username(self, username):
		user_obj = User.query.filter_by(username= username.data).first()
		if user_obj is not None:
			raise ValidationError("This username is taken, please pick any other username")
		
	def validate_email_addr(self, emailadrr):
		user_obj = User.query.filter_by(email = emailadrr.data).first()
		if user_obj is not None:
			raise ValidationError("This email address is already registered by a user, please use any other email")
	
	# important tip below :
	#When you add any methods that match the pattern validate_<field_name>, WTForms takes those as custom validators and invokes them in addition to the stock validators. 