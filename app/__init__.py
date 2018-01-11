from flask import Flask
from config import Config

app_instance = Flask(__name__)
app_instance.config.from_object(Config)		# setting the Config class from config.py module in our flask app object (app_instance)
											# NOW our flask app (or our app_instance) knows where to look for config variables (i.e in object of Config class)
from app import routes 	# this app meams app naam ka package i.e our directory which is named app