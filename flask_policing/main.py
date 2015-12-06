from flask import Flask, request, session, g, redirect, url_for ,\
	abort, render_template, flash
import MySQLdb
import pprint
import matplotlib.pyplot as plt
import numpy as np 
import sys
from random import randint
from parse import *
import pylab
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


def english_legend(style):
	colors = {'b': 'Blue',
				'g': 'Green',
				'r': 'Red',
				'c': 'Cyan',
				'm': 'Magenta',
				'y': 'Yellow',
				'k': 'Black',
				'w': 'White'}

	line_styles = {'-': 'Solid line',
					'-.': 'Dotted and dashed line',
					'--': 'Dashed line',
					':': 'Finely dashed line'}

	legend_string = ''

	legend_string += colors[style[0]]
	legend_string += ', '

	remaining = style[1:]

	legend_string += line_styles[remaining]

	return legend_string	


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
				if param_1 in l_cols:
					label_query = "SELECT DISTINCT {0} FROM locations order by {0}".format(param_1)
				elif param_1 in p_cols:
					label_query = "SELECT DISTINCT {0} FROM participants order by {0}".format(param_1)
			
			if param_2 == 'category' or param_2 == 'descript':
				query_1 = "SELECT DISTINCT {0} FROM locations order by {0}".format(param_2)
			else:
				if param_2 in l_cols:
					query_1 = "SELECT DISTINCT {0} FROM locations order by {0}".format(param_2)
				elif param_2 in p_cols:
					query_1 = "SELECT DISTINCT {0} FROM participants order by {0}".format(param_2)

			# print "get expected labels"
			# print label_query
			expected_labels = list()
			cursor.execute(label_query)
			for row in cursor.fetchall():
				if row[0] != '':
					expected_labels.append(row[0])

			# print "get distinct labels"
			# print query_1
			cursor.execute(query_1)
			distinct = list()
			for row in cursor.fetchall():
				# print row
				if row[0] != '':
					distinct.append(row[0])

			distinct = custom_sort(distinct)

			if param_1 in l_cols:
				table = "locations"
			elif param_1 in p_cols:
				table = 'participants'

			print "query database for each graph's data"
			pp.pprint(distinct)
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


			# pp.pprint(graph_data)


			colors = ['b','g','r','c','m','y','k']			
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
				rects = plt.barh(ind + (width/2),values,align='center',color=colors)
				plt.yticks(ind + (width/2),labels)
				plt.xlabel('Frequency')
				plt.tick_params(axis='y',which='major',pad=15)
				plt.title('Frequency of {0} = {1}'.format(org_1,distinct[i]))
				plt.grid(True)

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
			for i in range(len(distinct)):
				key = distinct[i]
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

		print "N = {0}".format(org_2)

		if request.form['param_2'] == None or request.form['param_2'] == '':
			err = "No value provided for N"
			return render_template('top_records_results',error=err)



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
		err = "No value provided for N"
		return render_template('top_records_results.html',error=err)		

@app.route('/time_series')
def time_series():
	return render_template('time_series.html')

@app.route('/time_series_results',methods=['GET','POST'])
def time_series_results():
	print "Inside time_series_results. Got {0} request".format(request.method)
	if request.method == 'POST':
		# dir_path = 'static/images/graphs/'
		# for f in os.listdir(dir_path):
		# 	os.remove(dir_path + f)

		org_1 = request.form['param_1']
		org_2 = request.form['param_2']
		label_of_interest = convert[org_1]
		time_period = org_2

		# get distinct labels
		if label_of_interest in l_cols:
			table = "locations"
		elif label_of_interest in p_cols:
			table = 'participants' # can't get date from participants

		label_query = "select distinct {0} from {1}".format(label_of_interest,table)
		cursor.execute(label_query)
		labels = list()
		for row in cursor.fetchall():
			if row[0] != '':
				labels.append(row[0])


		# Sorted arrays to be used later for graphing
		labels = sorted(labels)
		time_periods = list()
		if time_period == "Hours":
			for i in range(24):
				time_periods.append(i)
		elif time_period == 'Months':
			for i in range(12):
				time_periods.append(i+1)
		elif time_period == "Years":
			for i in range(2003,2016):
				time_periods.append(i)
			# year = 2003
			# while year != 2016:
			# 	time_periods.append(str(year))
			# 	year += 1

		time_periods = sorted(time_periods)

		# set up the bins
		bins = dict()
		for period in time_periods:
			bins[period] = 0

		# Initialize each time_period's frequency dict
		label_data = dict()
		for label in labels:
			if label != '':
				label_data[label] = None

		# pp.pprint(label_data)

		test_list = list()
		# pp.pprint(labels)
		for label in labels:
			query = "select dates, {0} from locations where {0} = \'{1}\'".format(label_of_interest,label)
			cursor.execute(query)

			data_dict = dict()
			for i in range(len(time_periods)):
				data_dict[time_periods[i]] = 0

			# count = 0
			for row in cursor.fetchall():
				# count += 1
				params = parse("{month}/{day}/{year} {hour}:{minutes}",row[0])


				if time_period == "Hours":
					param = params['hour']
					data_dict[int(param)] += 1					
				elif time_period == "Months":
					param = params['month']
					data_dict[int(param)] += 1					
				elif time_period == "Years":
					param = params['year']
					data_dict[int(param)] += 1

			# print "count for {0} = {1}".format(label,count)
			
			change_to_tuples = list()
			for key in data_dict:
				change_to_tuples.append((key,data_dict[key]))

			test_list.append((label,sorted(change_to_tuples,key=lambda tup: tup[0])))
			label_data[label] = data_dict



		# pp.pprint(test_list)


		# Extract data to prepare for graphing
		colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
		line_styles = ['-','-.','--',':']

		styles = list()
		for color in colors:
			for line_style in line_styles:
				styles.append(color + line_style)

		pp.pprint(test_list)
		largest = 0
		used_styles = list()
		legend = list()

		# try:
		# 	img_url = 'static/images/graphs/time_series.png'
		# 	os.remove(img_url)
		# except OSError:
		# 	pass

		fig, ax = plt.subplots()
		for pair in test_list:
			data_points = pair[1]
			x = list()
			y = list()		
			for i in range(len(data_points)):
				x.append(data_points[i][0])
				y.append(data_points[i][1])


			if max(y) > largest:
				largest = max(y)

			style = styles[0]
			while style in used_styles:
				if len(used_styles) == len(styles):
					used_styles = list()
					break

				style = styles[randint(0,len(styles))-1]

			ax.plot(x,y,style,label=pair[0])
			used_styles.append(style)

			legend.append((pair[0],english_legend(style)))
	
		# pp.pprint(legend)

		plt.ylabel('Frequency')
		plt.xlabel('Time')
		plt.title('Count of Crime by {0}'.format(org_1))
		plt.grid(True)


		org_1 = replace_characters(org_1)
		time_period = replace_characters(time_period)
		img_url = 'static/images/graphs/time_series_{0}_{1}.png'.format(org_1,time_period)
		print img_url
		plt.savefig(img_url)


		return render_template('time_series_results.html',url=img_url,col_1=org_1,legend=legend,type=time_period)
	else:
		return render_template('time_series_results.html')

@app.route('/gallery')
def galler():
	return render_template("gallery.html")

@app.route('/search_main')
def search_main():
	tagline = '''You want it; we have it. 
				With the several types of retrieval provided, 
				you can start analyzing trends immediately.'''
	return render_template('search_main.html',title='Search Main',tagline=tagline)






if __name__ == '__main__':
	app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
	app.run(debug=True)


