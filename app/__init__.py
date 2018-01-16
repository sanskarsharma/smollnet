from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from flask_login import LoginManager


app_instance = Flask(__name__)
app_instance.config.from_object(Config)			# setting the Config class from config.py module in our flask app object (app_instance)
												# NOW our flask app (or our app_instance) knows where to look for config variables (i.e in object of Config class)

db_instance = SQLAlchemy(app_instance)
migrate = Migrate(app_instance, db_instance)
login_manager_instance = LoginManager(app_instance)

from app import routes, models				 	# this "app" means app naam ka package i.e our directory which is named app
