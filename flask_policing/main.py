from flask import Flask, request, session, g, redirect, url_for ,\
	abort, render_template, flash
import MySQLdb
import pprint
import matplotlib.pyplot as plt
import numpy as np 
import sys
from parse import *
from pylab import *
import os

'''
To-Do:
	- Drop-down menu selections
	- Tables
	- Graphs
	- Random
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

p_cols = ["officer_age",
			"officer_ethnicity",
			"officer_gender",
			"offender_age",
			"offender_ethnicity",
			"offender_gender",
			"offender_income"]

l_cols = ["descript",
			"dates",
			"day_of_week",
			"pd_district",
			"resolution",
			"address",
			"category"]

days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

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


def correct_values(coordinates,expected_labels):
	existing_labels = list()
	for pair in coordinates:
		existing_labels.append(pair[0])

	for label in expected_labels:
		if label not in existing_labels:
			coordinates.append((label,long(0)))



	return coordinates

def custom_sort(container):
	if container[0] in days:
		return days
	else:
		return container


def replace_characters(word):

	replace_chars = [' ','/']
	for char in replace_chars:
		if char in word:
			word = word.replace(char,'_')
	return word


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
	return render_template('search.html')

@app.route('/search_results',methods=['GET','POST'])
def search_results():
	print "We got a {0} request".format(request.method)
	if request.method == 'POST':
		org_1 = request.form['param_1']
		org_2 = request.form['param_2']
		param_1 = convert[org_1]
		param_2 = convert[org_2]

		if org_1 == org_2:
			err = "Cannot compare a label with itself"
			return render_template('search_results.html',error=err)
		else:
			if param_1 == 'category' or param_1 == 'descript':
				label_query = "SELECT DISTINCT {0} FROM locations order by {0}".format(param_1)
			else:
				label_query = "SELECT DISTINCT {0} FROM locations, participants order by {0}".format(param_1)
			
			if param_2 == 'category' or param_2 == 'descript':
				query_1 = "SELECT DISTINCT {0} FROM locations order by {0}".format(param_2)
			else:
				query_1 = "SELECT DISTINCT {0} FROM locations, participants order by {0}".format(param_2)

			print "get expected labels"
			print label_query
			expected_labels = list()
			cursor.execute(label_query)
			for row in cursor.fetchall():
				expected_labels.append(row[0])

			print "get distinct labels"
			print query_1
			cursor.execute(query_1)
			distinct = list()
			for row in cursor.fetchall():
				print row
				distinct.append(row[0])

			distinct = custom_sort(distinct)

			if param_1 in l_cols:
				table = "locations"
			elif param_1 in p_cols:
				table = 'participants'

			print "query database for each graph's data"
			# pp.pprint(distinct)
			graph_data = dict()
			for item in distinct:
				query_2 = '''SELECT {0}, COUNT(*) FROM {1} 
							WHERE {2} = \'{3}\' 
							GROUP BY {0}'''.format(param_1,table,param_2,item)

				print query_2
				# print item
				coordinates = list()	
				try:
					cursor.execute(query_2)
				except:
					e = sys.exc_info()[0]
					pp.pprint(e)
					err = "Looks like something went wrong"
					return render_template('search_results.html',error=err)

				# print "getting coordinates"
				for row in cursor.fetchall():
					coordinates.append(row)

				# pp.pprint(coordinates)			


				if len(coordinates) != len(distinct):
					coordinates = correct_values(coordinates,expected_labels)
				

				graph_data[item] = sorted(coordinates,key=lambda tup: tup[1])


			pp.pprint(graph_data)

			print "graphing the data"
			# Graph the data
			for i in range(len(distinct)):
				test = graph_data[distinct[i]]


				labels = list()
				values = list()
				for tup in test:
					labels.append(tup[0])
					values.append(tup[1])

				labels = tuple(labels)
				values = tuple(values)

				# pp.pprint(len(labels))
				# pp.pprint(len(values))

				plt.figure()
				N = len(labels)
				ind = np.arange(N)
				width = 2
				rects = barh(ind + (width/2),values,align='center')
				yticks(ind + (width/2),labels)
				xlabel('Frequency')
				tick_params(axis='y',which='major',pad=15)
				title('Frequency of {0} = {1}'.format(org_1,distinct[i]))
				grid(True)

				plt.autoscale()
				plt.tight_layout()

				one = distinct[i]
				distinct[i] = replace_characters(distinct[i])

				url = "static/images/graphs/{0}.png".format(distinct[i])
				two = url
				plt.savefig("static/images/graphs/{0}.png".format(distinct[i]))
				plt.close()
			
			print "creating image urls"
			image_urls = list()
			for key in graph_data:
				key = replace_characters(key)

				url = "static/images/graphs/{0}.png".format(key)
				image_urls.append("static/images/graphs/{0}.png".format(key))

			return render_template('search_results.html',urls=image_urls)

	else:
		return render_template('search_results.html')

@app.route('/top_records')
def top_records():
	return render_template('top_records.html')

@app.route('/top_records_results',methods=['GET','POST'])
def top_records_results():
	print "Inside top_records_results. Got {0} request".format(request.method)
	if request.method == 'POST':
		org_1 = request.form['param_1']
		org_2 = request.form['param_2']
		label_of_interest = convert[org_1]

		try:		
			N = int(org_2)
		except:
			err = "Could not convert N into an integer"
			return render_template('top_records_results.html',error=err)

		if label_of_interest in l_cols:
			table = "locations"
		elif label_of_interest in p_cols:
			table = 'participants'

		query = '''select {0}, count(*) as num from {1}
					group by {0} order by num DESC'''.format(label_of_interest,table)

		print query

		cursor.execute(query)
		count = 0
		results = list()
		for row in cursor.fetchall():
			results.append(row)
			count += 1

		pp.pprint(results)
		return render_template('top_records_results.html',col_1=org_1,results=results[0:N])

	else:
		return render_template('top_records_results.html')		

@app.route('/time_series')
def time_series():
	return render_template('time_series.html')

@app.route('/time_series_results',methods=['GET','POST'])
def time_series_results():
	print "Inside time_series_results. Got {0} request".format(request.method)
	if request.method == 'POST':
		org_1 = request.form['param_1']
		org_2 = request.form['param_2']
		label_of_interest = convert[org_1]
		time_period = org_2

		# get distinct labels
		if label_of_interest in l_cols:
			table = "locations"
		elif label_of_interest in p_cols:
			table = 'participants'

		label_query = "select distinct {0} from {1}".format(label_of_interest,table)
		cursor.execute(label_query)
		labels = list()
		for row in cursor.fetchall():
			labels.append(row[0])


		# Sorted arrays to be used later for graphing
		labels = sort(labels)
		time_periods = list()
		if time_period == "Hours in a day":
			for i in range(24):
				time_periods.append(str(i))
		elif time_period == "Years":
			year = 2003
			while year != 2016:
				time_periods.append(str(year))
				
		time_periods = sort(time_periods)

		# set up the bins
		bins = dict()
		for period in time_periods:
			bins[period] = 0

		# Initialize each time_period's frequency dict
		label_data = dict()
		for label in labels:
			if label != '':
				label_data[label] = bins


		# Issue the query for data
		query = "select dates, {0} from {1}".format(label_of_interest,table)
		cursor.execute(query)

		
		# Sort each data point into its appropriate bin
		for row in cursor.fetchall():
			if row[0] != '' and row[1] != '':
				date = row[0]
				label = row[1]

				params = parse("{month}/{day}/{year} {hour}:{minutes}",date)

				label_data[label][params['year']] += 1

		pp.pprint(label_data)

		# Extract data to prepare for graphing

		
		# pp.pprint(x_labels)




		return render_template('time_series_results.html')


@app.route('/search_main')
def search_main():
	tagline = '''You want it; we have it. 
				With the several types of retrieval provided, 
				you can start analyzing trends immediately.'''
	return render_template('search_main.html',title='Search Main',tagline=tagline)






if __name__ == '__main__':
	app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
	app.run(debug=True)


