from flask import abort
from flask import Blueprint 
from flask import current_app
from flask import Flask
from flask import jsonify

from src.db.db import get_db

bp = Blueprint('api', __name__, url_prefix='/api')

def dict_factory(cursor, row):
	""" Create an object to access columns by name """
	d = {}
	# Iterate over the column names
	for idx, col in enumerate(cursor.description):
		# Create a new object
		d[col[0]] = row[idx]
	return d


@bp.route('/price')
def price():
	""" Return JSON """
	db = get_db()
	# Convert to dictionary
	print(type(dict_factory))
	db.row_factory = dict_factory
	# List of price data
	with current_app.open_resource('db/sql/query.sql') as f:
		# Remove first entry from price table
		with current_app.open_resource('db/sql/delete.sql') as y:
			price = db.execute(y.read().decode('utf8'))
			price = db.execute(f.read().decode('utf8')).fetchall()
			if price is None:
	 			abort(404, description="Resource not found")
			else:
				return jsonify(price)
