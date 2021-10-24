import csv
import datetime
import json
import os
import sqlite3
import urllib.request

import click
from flask import current_app, g
from flask.cli import with_appcontext

SPREADSHEET = 'src/db/data/ETH.csv'
SECRET_KEY = os.environ.get('SECRET_KEY')

def get_db():
	""" Connect to database """
	if 'db' not in g:
		g.db = sqlite3.connect(
			current_app.config['DATABASE'],
			detect_types=sqlite3.PARSE_DECLTYPES
		)
		g.db.row_factory = sqlite3.Row
	return g.db

def close_db(e=None):
	""" Close database connection """
	db = g.pop('db', None)

	if db is not None:
		db.close()

def init_db():
	""" Clear existing data and create new tables """
	db = get_db()

	with current_app.open_resource('db/sql/schema.sql') as f:
		db.executescript(f.read().decode('utf8'))

def insert_db():
	""" Add CSV data into database """
	db = get_db()
	cur = db.cursor()
	file = open(SPREADSHEET)	
	contents = csv.reader(file)

	with current_app.open_resource('db/sql/insert.sql') as f:
		cur.executemany(f.read().decode('utf8'), contents)
		db.commit()

def data_db():
	""" Query API and add data to CSV """
	f = urllib.request.Request('https://min-api.cryptocompare.com/data/v2/histoday?fsym=ETH&tsym=USD&limit=2000', 
								data=None, headers={'authorization': SECRET_KEY})
	with urllib.request.urlopen(f) as r:
		try:
			# Parse json response
			data = json.loads(r.read().decode('utf-8'))
			# Dict write csv module
			with open(SPREADSHEET, 'w', newline='') as csvfile:
				# Sequence of keys that specify the write order to file 
				fieldnames = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
				# Dict write csv module
				writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
				# Create a dictionary of fieldnames
				writer.writeheader()
				# Iterate over the data list
				for x in data['Data']['Data']:
					# Convert time stamp
					x['time'] = datetime.datetime.utcfromtimestamp(x['time']).isoformat()[0:10]
					# Write to file
					writer.writerow({'Date': x['time'],'Open': x['open'], 'High': x['high'], 
									'Low': x['low'], 'Close': x['close'], 'Adj Close': x['close'],
									'Volume': x['volumefrom']})

		except Exception as e:
			print("Error getting coin information %s" % str(e))
			return None	

	
@click.command('init-db')
@with_appcontext
def init_db_command():
	"""Clear the existing data and create new tables."""
	init_db()
	click.echo('Initialized the database.')

@click.command('insert-db')
@with_appcontext
def insert_db_command():
	""" Add csv file to database """
	insert_db()
	click.echo('Data added successfully')

@click.command('data-db')
@with_appcontext
def data_db_command():
	""" Query API and add data to CSV """
	data_db()
	click.echo('Upload to CSV complete')

@click.command('db')
@with_appcontext
def db_command():
	""" Run all DB commands """
	init_db()
	data_db()
	insert_db()
	click.echo('Database operational')

def init_app(app):
	""" Register database functions with the Flask app """
	app.teardown_appcontext(close_db)
	app.cli.add_command(init_db_command)
	app.cli.add_command(insert_db_command)
	app.cli.add_command(data_db_command)
	app.cli.add_command(db_command)