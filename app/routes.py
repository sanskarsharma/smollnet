from app import app_instance

@app_instance.route('/')
@app_instance.route('/index')		# these are called decorators
def index():		# this is called a view function
	return "hello from flasky"
