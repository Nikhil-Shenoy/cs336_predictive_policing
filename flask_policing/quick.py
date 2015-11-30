from flask import Flask, request, session, g, redirect, url_for ,\
	abort, render_template, flash
import MySQLdb
import pprint

app = Flask(__name__)
host = 'policing.cke0kirlh7a4.us-east-1.rds.amazonaws.com'
username = 'nikhil'
password = 'cs336shenoy'
dbname = 'BarBeerDrinker'

# host = 
# username = 'master'
# password = 'password'
# dbname = 'Final_Pred_Pol'

pp = pprint.PrettyPrinter()

# DB configuration
db = MySQLdb.connect(user=username, passwd=password, host=host, db=dbname)
cursor = db.cursor()

@app.route('/')
def home():
	return render_template('main.html')


@app.route('/about')
def about():
	return render_template('layout.html')

@app.route('/search')
def search():
	cursor.execute('SELECT * FROM sells')
	entries = [dict(bar=row[0], beer=row[1], price=row[2]) for row in cursor.fetchall()]
	return render_template('search.html',entries=entries)


if __name__ == '__main__':
	app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
	app.run(debug=True)