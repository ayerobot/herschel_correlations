#separate line plotting function that can be run from the command line
import matplotlib.pyplot as plt
import sys
from herschel_correlations import data_as_dicts, convert_dicts, load_objdata
import numpy as np
import scipy.stats as stats

#syntax: input Herschel data file (PACS, SPIRE, or both), the CSV file with the bolometric properties and object type,
#and what you want to graph. Either two lines, or if the second line is "Lbol" or "Tbol", it'll graph that. 

def plot_lines(line1, line2, targets, data):
	line1_points = []
	line2_points = []
	names = []
	#extracting all relevant data
	for targ in targets:
		if line1 in data[targ].keys() and line2 in data[targ].keys() and data[targ][line1]['SNR'] > 3 and data[targ][line2]['SNR'] > 3:
			line1_points.append(data[targ][line1]['Str(W/cm2)'])
			line2_points.append(data[targ][line2]['Str(W/cm2)'])
			names.append(targ)

	fig = plt.figure()
	ax = fig.add_subplot(111)
	sc = ax.scatter(np.log(line1_points), np.log(line2_points))
	for i in range(0, len(names)):
		ax.annotate(names[i], (np.log(line1_points[i]) , np.log(line2_points[i])))

	r, p = stats.pearsonr(line1_points, line2_points)

	plt.title(line1 + " vs " + line2 + " intensity, r =  " + str(r))
	plt.xlabel("log " + line1 + " strength (W/cm2))")
	plt.ylabel("log " + line2 + " strength (W/cm2))")
	#plt.xlim([np.min(line1_points)*0.80, np.max(line1_points)*1.2])
	#plt.ylim([np.min(line2_points)*0.80, np.max(line2_points)*1.2])	
	plt.show()

def plot_lines_from_datafile(datafile, line1, line2, types_file):
	#loading data to plot 
	data_unprocessed = data_as_dicts(datafile)
	data = convert_dicts(data_unprocessed)
	acceptable_types = ["protostar", "Fuor"] #hardcoded
	targ_data = load_objdata(types_file)
	#targets = get_targets(data_unprocessed)
	targets = data.keys() #the first level of the dictionary is populated by target names 
	targets_filtered = [target for target in targets if targ_data[target]['type'] in acceptable_types]
	plot_lines(line1, line2, targets_filtered, data)

def plot_property_from_datafile(datafile, line1, prop, types_file):
	#loading data to plot 
	data_unprocessed = data_as_dicts(datafile)
	data = convert_dicts(data_unprocessed)
	acceptable_types = ["protostar", "Fuor"] #hardcoded
	targ_data = load_objdata(types_file)
	targets = data.keys() #the first level of the dictionary is populated by target names 
	targets_filtered = [target for target in targets if targ_data[target]['type'] in acceptable_types]
	plot_property(line1, prop, targets_filtered, targ_data, data)


def plot_property(line1, prop, targets, targ_data, data):
	line1_points = []
	property_points = []
	names = []
	#extracting all relevant data
	for targ in targets:
		if line1 in data[targ].keys() and data[targ][line1]['SNR'] > 3:
			line1_points.append(data[targ][line1]['Str(W/cm2)'])
			property_points.append(targ_data[targ][prop])
			names.append(targ)

	fig = plt.figure()
	ax = fig.add_subplot(111)
	sc = ax.scatter(np.log(line1_points), np.log(property_points))
	for i in range(0, len(names)):
		ax.annotate(names[i], (np.log(line1_points[i]) , np.log(property_points[i])))

	r, p = stats.pearsonr(line1_points, property_points)

	plt.title(line1 + " vs " + line2 + " intensity, r =  " + str(r))
	plt.xlabel("log " + line1 + " strength (W/cm2))")
	plt.ylabel("log " + prop)
	#plt.xlim([np.min(line1_points)*0.80, np.max(line1_points)*1.2])
	#plt.ylim([np.min(line2_points)*0.80, np.max(line2_points)*1.2])	
	plt.show()


if __name__ == "__main__":
	if len(sys.argv) != 5:
		print "plot_lines.py data_file target_properties line1 line2"
	else:
		datafile = sys.argv[1]
		target_props = sys.argv[2] #the bolometric properties and target type
		line1 = sys.argv[3]
		line2 = sys.argv[4]
		if line2 == "Lbol" or line2 == "Tbol":
			plot_property_from_datafile(datafile, line1, line2, target_props)
		else:
			plot_lines_from_datafile(datafile, line1, line2, target_props)