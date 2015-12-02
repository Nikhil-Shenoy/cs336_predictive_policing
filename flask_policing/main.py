from flask import Flask, request, session, g, redirect, url_for ,\
	abort, render_template, flash
import MySQLdb
import pprint

'''
To-Do:
	- Drop-down menu selections
	- Tables
	- Graphs
	- Random
	- Log ins
'''


app = Flask(__name__)
# host = 'policing.cke0kirlh7a4.us-east-1.rds.amazonaws.com'
# username = 'nikhil'
# password = 'cs336shenoy'
# dbname = 'BarBeerDrinker'

host = 'sfpp.c6vo9fxyykyv.us-east-1.rds.amazonaws.com'
username = 'DreamTeam'
password = 'rurahrah'
dbname = 'sfpp'

participant_params = ["Officer Age",
					"Officer Ethnicity",
					"Officer Gender",
					"Offender Age",
					"Offender Ethnicity",
					"Offender Gender",
					"Offender Income"]

location_params = ["Description",
					"Date",
					"Day of the Week",
					"Police Department District",
					"Resolution",
					"Address",
					"Category"]

convert = dict()
convert['Officer Age'] = 'officer_age'
convert['Officer Ethnicity'] = 'officer_ethnicity'
convert['Officer Gender'] = 'officer_gender'
convert['Offender Age'] = 'offender_age'
convert['Offender Ethnicity'] = 'offender_ethnicity'
convert['Offender Gender'] = 'offender_gender'
convert['Offender Income'] = 'offender_income'
convert['Description'] = 'descript'
convert['Date'] = 'dates'
convert['Day of the Week'] = 'day_of_week'
convert['Police Department District'] = 'pd_district'
convert['Resolution'] = 'resolution'
convert['Address'] = 'address'
convert['Category'] = 'category'

pp = pprint.PrettyPrinter()

# DB configuration
db = MySQLdb.connect(user=username, passwd=password, host=host, db=dbname)
cursor = db.cursor()

@app.route('/')
def home():
	return render_template('index.html')


@app.route('/about')
def about():
	tagline = "A little bit about ourselves"
	return render_template('about.html',title="Our Team", tagline=tagline)

@app.route('/search')
def search():
	cursor.execute('SELECT * FROM participants')

	entries = list()
	for row in cursor.fetchall():
		data = dict()
		data['incident_id'] = row[0]
		data['officer_age'] = row[1]
		data['officer_ethnicity'] = row[2]
		data['officer_gender'] = row[3]
		data['offender_age'] = row[4]
		data['offender_ethnicity'] = row[5]
		data['offender_gender'] = row[6]
		data['offender_income'] = row[7]
		data['category'] = row[8]
		data['descript'] = row[9]

		entries.append(data)

	return render_template('search.html',entries=entries)
	# return render_template('search.html',)

@app.route('/search_results',methods=['GET','POST'])
def search_results():
	print "We got a {0} request".format(request.method)
	if request.method == 'POST':
		query_type = request.form['query_type']
		query_parameter = request.form['query_parameter']

		query = ""
		if query_type == "Unique":
			query += "SELECT DISTINCT {0} from ".format(convert[query_parameter])
			if query_parameter in participant_params:
				query += "participants"
			elif query_parameter in location_params:
				query += "location"
		elif query_type == "Frequency":
			query += "SELECT COUNT({0}) from ".format(convert[query_parameter])
			if query_parameter in participant_params:
				query += "participants"
			elif query_parameter in location_params:
				query += "location"


		print query
		cursor.execute(query)
		result = cursor.fetchall()
		print type(result)
		print len(result)

		if query_type == "Frequency": # We know it was a COUNT query
			return render_template('search_results.html',flag="frequency",final_count = result[0], parameter=query_parameter)
		elif query_type == "Unique":
			pp.pprint(result)
			return render_template('search_results.html',flag="unique",parameter=query_parameter,results=result)
	else:
		return render_template('search_results.html')

if __name__ == '__main__':
	app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
	app.run(debug=True)
