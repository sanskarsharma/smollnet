from flask import Flask

app_instance = Flask(__name__)

from app import routes 	# this app meams app naam ka package i.e our directory which is named app