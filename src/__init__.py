import os

from flask import Flask

def create_app(test_config=None, instance_relative_config=True):
	""" Create and configure an application instance """
	app = Flask(__name__)
	# Update config ignoring items with non-upper keys
	app.config.from_mapping( 
		# Path to the instance folder
		DATABASE=os.path.join(app.instance_path, 'src.sqlite')
	)

	if test_config is None:
		# Load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		# Load the test config if passed in
		app.config.from_mapping(test_config)

	# Ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# Register the database commands
	from .db import db
	db.init_app(app)

	# Register the api routes
	from src import api
	app.register_blueprint(api.bp)

	
	return app