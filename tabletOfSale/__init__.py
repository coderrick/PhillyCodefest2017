from flask import Flask, g
import sqlite3

app=Flask(__name__)
app.config.from_envvar('TOSOS_SETTINGS')

def get_db():
	db=getattr(g, '_database', None)
	if db is None:
		db=g._database=sqlite3.connect(app.config['DATABASE'])
	return db

@app.teardown_appcontext
def close_connection(exception):
	db=getattr(g, '_database', None)
	if db is not None:
		db.close()

import tabletOfSale.views
