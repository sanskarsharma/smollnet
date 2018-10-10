from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from flask_login import LoginManager

import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from celery import Celery
import tweepy

app_instance = Flask(__name__)
app_instance.config.from_object(Config)			# setting the Config class from config.py module in our flask app object (app_instance)
app_instance.debug = False												# NOW our flask app (or our app_instance) knows where to look for config variables (i.e in object of Config class)

# adding below config for 'lost connection to mysql' on pyaw error
app_instance.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app_instance.config['SQLALCHEMY_POOL_TIMEOUT'] = 20


twitter_auth = tweepy.OAuthHandler(app_instance.config['TWITTER_CONSUMER_KEY'], app_instance.config['TWITTER_CONSUMER_SECRET'])
twitter_auth.set_access_token(app_instance.config['TWITTER_ACCESS_TOKEN'], app_instance.config['TWITTER_ACCESS_TOKEN_SECRET'])

twitter_api = tweepy.API(twitter_auth)

mail_instance = Mail(app_instance)
bootstrap = Bootstrap(app_instance)
moment = Moment(app_instance)

# celery
celery = Celery(app_instance.name, broker=app_instance.config['CELERY_BROKER_URL'])
celery.conf.update(app_instance.config)

db_instance = SQLAlchemy(app_instance)
migrate = Migrate(app_instance, db_instance)
login_manager_instance = LoginManager(app_instance)
login_manager_instance.login_view = "login"		# this "login" is the name of our view function(in routes) which handles login of user
												# we are setting this to use the "require login for certain pages" functionality given by flask_login extention
from app import routes, models, errors			 	# this "app" means app naam ka package i.e our directory which is named app

if not app_instance.debug:

		# to be used when using a mail server along with flask server
		####  FOR SENDING SERVER ERROR MAILS TO SITE ADMINS
		# if app_instance.config['MAIL_SERVER']:
		# 	auth = None
		# 	if app_instance.config['MAIL_USERNAME'] or app_instance.config['MAIL_PASSWORD']:
		# 		auth = (app_instance.config['MAIL_USERNAME'], app_instance.config['MAIL_PASSWORD'])
		# 	secure = None
		# 	if app_instance.config['MAIL_USE_TLS']:
		# 		secure = ()
		# 	mail_handler = SMTPHandler(
		# 		mailhost=(app_instance.config['MAIL_SERVER'], app_instance.config['MAIL_PORT']),
		# 		fromaddr='no-reply@' + app_instance.config['MAIL_SERVER'],
		# 		toaddrs=app_instance.config['ADMINS'], subject='Microblog Failure',
		# 		credentials=auth, secure=secure)
		# 	mail_handler.setLevel(logging.ERROR)
		# 	app_instance.logger.addHandler(mail_handler)


		# below code is for writing log files
		if not os.path.exists('logs'):
			os.mkdir('logs')
		file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
		file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s \n \t\t [in %(pathname)s:%(lineno)d]'))
		file_handler.setLevel(logging.INFO)
		app_instance.logger.addHandler(file_handler)

		app_instance.logger.setLevel(logging.INFO)
		app_instance.logger.info('Microblog startup')
