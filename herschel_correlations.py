import numpy as np
import matplotlib.pyplot as plt
import itertools
import scipy.stats as stats
import csv
import sys

#imports the lines file as a list of dictionaries
#each line corresponds to a dictionary in the list; each column corresponds to a key
def data_as_dicts(filepath):
	dicts = []
	with open(filepath) as datafile:
		firstline = datafile.readline()
		keys = firstline.split()
		for line in datafile.readlines():
			line_list = line.split()
			dct = {}
			#puts all keys in the dictionary with their corresponding value
			for key, val in zip(keys, line_list): 
				val = float(val) if is_float(val) else val
				dct[key] = val
			dicts.append(dct)

	return dicts

#loads the object type as a dictionary 
#keys are object name, values are dictionaries with object properties 
def load_objdata(filepath):
	types = {}
	with open(filepath, 'rU') as datafile:
		reader = csv.reader(datafile)
		lines = [row for row in reader if row[0] != "target_name" and row[0] != "" ]
		for line in lines:
			types[line[0]] = {}
			types[line[0]]['type'] = line[1]
			types[line[0]]['Lbol'] = float(line[2])
			types[line[0]]['Tbol'] = float(line[3])
	return types


#convert the list of dictionaries to a large dictionary in the format:
#dict[targetname][line] = {dictionary of data}
def convert_dicts(dicts):
	results = {}
	for dat in dicts:
		if dat['Object'] not in results.keys():
			results[dat['Object']] = {}
		results[dat['Object']][dat['Line']] = dat #target name and object will be redundant here
	return results


#gets the lab wavelength of every unique line, return dictionary
def get_labwl(data):
	wl = {}
	for line in data:
		wl[line['Line']] = line['LabWL(um)']
	return wl


#determine if it's possible to convert the value to a float
def is_float(string):
	try:
		float(string)
		return True
	except: 
		return False

#iterates through the list, gets all unique line names 
def get_line_names(data):
	names = set()
	[names.add(line['Line']) for line in data]
	return names

def get_targets(data):
	targets = set()
	[targets.add(line['Object']) for line in data]
	return targets

#more efficient method of finding pair correlations. First loading data as a 2d dictionary 
#this enables O(1) access to information without looping through the data array every time
def compare_all_lines(data, names, targets, threshold, labwls):
	pairs = itertools.combinations(names, 2)
	results = []
	for line1, line2 in pairs:
		#gets the strength of each line
		#TODO: take s2n and negatives into account here without mismatching lengths
		
		#need to iterate through targets, in case one line is detected in the target but the other isn't
		line1_str = []
		line2_str = []
		for targ in targets:
			if line1 in data[targ].keys() and line2 in data[targ].keys() and data[targ][line1]['SNR'] > 3 and data[targ][line2]['SNR'] > 3:
				line1_str.append(data[targ][line1]['Str(W/cm2)'])
				line2_str.append(data[targ][line2]['Str(W/cm2)'])
		line1_arr = np.array(line1_str)
		line2_arr = np.array(line2_str)
		if len(line1_arr) > 0 and len(line2_arr) > 0:
			r, p = stats.pearsonr(line1_arr, line2_arr)
			if np.abs(r) >= threshold: 
				if np.isnan(p): #if not a number, just save as 0
					p = 0.0
				print line1, line2, r, p, len(line1_arr)
				#print "correlation detected between " + line1 + " and " + line2 + ", r = " + str(r)
				results.append({'line1':line1, 'line1_wl(um)': labwls[line1], 'line2':line2, 'line2_wl(um)': labwls[line2], 'r':r, 'p':p, 'num_detections': len(line1_arr)}) 

	return results



#save as CSV file
def save_data(data, outfile):
	with open(outfile, 'w') as csvfile:
		#fieldnames = data[0].keys()
		fieldnames = ['line1', 'line1_wl(um)', 'line2', 'line2_wl(um)', 'r', 'p', 'num_detections'] #hardcoding
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for result in data:
			writer.writerow(result)

#loads from CSV data file
#returns list of dictionaries
def load_data(filepath):
	data = []
	with open(filepath) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			#converting to floats
			row['r'] = float(row['r'])
			row['p'] = float(row['p'])
			row['num_detections'] = float(row['num_detections'])
			data.append(row)
	return data

#compare the relationship between a property (either "Lbol" or "Tbol" for now) 
#and all lines
def lines_vs_property(prop_name, targ_data, line_data, targets, line_names, labwls, threshold = 0.0):
	results = []
	for line in line_names:
		line_str = []
		prop = []
		for targ in targets:
			#filtering out protostars without that property recorded
			if line in line_data[targ].keys() and line_data[targ][line]['SNR'] > 3 and targ_data[targ][prop_name] > 0: 
				line_str.append(line_data[targ][line]['Str(W/cm2)'])
				prop.append(targ_data[targ][prop_name])

		if len(line_str) > 0 and len(prop) > 0:
			r, p = stats.pearsonr(line_str, prop)
			if np.abs(r) >= threshold:
				p = 0.0 if np.isnan(p) else p 
				print line, prop_name, r, p, len(line_str)
				#using slightly erroneous labels to ensure compatibility with 
				#saving function
				results.append({'line1':line, 'line1_wl(um)': labwls[line], 'line2':prop_name, 'line2_wl(um)':0.0, 'r':r, 'p':p, 'num_detections': len(line_str) })

	return results
#for convenience 
def exclusive_or(a, b):
	return (a and not b) or (not a and b)

#swaps the wavelength and line between a correlation dictionary
def swap_lines(cor):
	old_line2 = cor['line2']
	old_line2_wl = cor['line2_wl(um)']
	cor['line2_wl(um)'] = cor['line1_wl(um)']
	cor['line2'] = cor['line1']
	cor['line1'] = old_line2
	cor['line1_wl(um)'] = old_line2_wl
	return cor 

#correlations between lines where one line does not contain the prefix
#example: find correlations betweel all CO lines and all non-CO lines
def compare_different_lines(data, prefix, threshold):
	correlations = []
	for cor in data:
		if exclusive_or(not cor['line1'].startswith(prefix), not cor['line2'].startswith(prefix)) and np.abs(cor['r']) > threshold:
			#ensuring that the line with the prefix is in line1, for convenience's sake
			if cor['line2'].startswith(prefix):
				cor2 = swap_lines(cor)
			correlations.append(cor2)
	return correlations

#assembling everything together into one function that just takes filepaths 
#not filtering on a threshold by default, but it's an optional parameter 
def correlations_from_datafile(filepath, outfile, targ_data, acceptable_types, threshold = 0.0):
	targ_data = load_objdata(targ_data)
	data_unprocessed = data_as_dicts(filepath)
	data = convert_dicts(data_unprocessed)
	names = get_line_names(data_unprocessed)
	#targets = get_targets(data_unprocessed)
	targets = data.keys() #the first level of the dictionary is populated by target names 
	targets_filtered = [target for target in targets if targ_data[target]['type'] in acceptable_types]
	wlnames = get_labwl(data_unprocessed)
	results = compare_all_lines(data, names, targets_filtered, threshold, wlnames)
	save_data(results, outfile)

#computing all correlations between a property and 
def prop_correlations_from_datafile(filepath, prop, targ_datapath, acceptable_types, outfile, threshold_str = 0.0):
	targ_data = load_objdata(targ_datapath)
	data_unprocessed = data_as_dicts(filepath)
	line_data = convert_dicts(data_unprocessed)
	names = get_line_names(data_unprocessed)
	targets = line_data.keys() #the first level of the dictionary is populated by target names 
	targets_filtered = [target for target in targets if targ_data[target]['type'] in acceptable_types]
	wlnames = get_labwl(data_unprocessed)
	results = lines_vs_property(prop, targ_data, line_data, targets_filtered, names, wlnames)
	save_data(results, outfile)

#mostly intended to be used in CO vs CO 13 correlations.
#given two prefixes and a target, will seek out matching adjacent J-values (i.e. 4-3, 15-14, etc)
#from j = 4 to j = 20 
def ratio_vs_j(line1_prefix, line2_prefix, data, target):
	ratios = []
	j = []
	for i in range(4, 20): #acceptable j-range hardcoded
		line1 = line1_prefix + str(i) + "-" + str(i - 1)
		line2 = line2_prefix + str(i) + "-" + str(i - 1)
		if line1 in data[target].keys() and line2 in data[target].keys() and data[target][line1]['SNR'] > 3 and data[target][line2]['SNR'] > 3:
			line1_str = data[target][line1]['Str(W/cm2)']
			line2_str = data[target][line2]['Str(W/cm2)']
			ratio = line1_str/line2_str
			ratios.append(ratio)
			j.append(i)
	return ratios, j

#specialized plotting function
#saves by default instead of showing
#saves with target name 
def plot_ratio_vs_j(ratios, ratio_name, j, target, output_folder = None):
	fig = plt.figure()
	ax = fig.add_subplot(111)
	sc = ax.scatter(j, ratios)
	r, p = stats.pearsonr(j, ratios)
	plt.title(ratio_name + " vs J for " + target +  " r =  " + str(r))
	plt.ylabel(ratio_name)
	plt.xlabel("J")
	#plt.xlim([np.min(line1_points)*0.80, np.max(line1_points)*1.2])
	#plt.ylim([np.min(line2_points)*0.80, np.max(line2_points)*1.2])	
	if output_folder:
		plt.savefig(output_folder + target)
	else:
		plt.show()
	
#putting the previous two together
def ratio_from_file(datafile, line1_prefix, line2_prefix, target):
	#loading data to plot 
	data_unprocessed = data_as_dicts(datafile)
	data = convert_dicts(data_unprocessed)
	ratios, j = ratio_vs_j(line1_prefix, line2_prefix, data, target)
	plot_ratio_vs_j(ratios, line1_prefix + "/" + line2_prefix, j, target)

if __name__ == "__main__":
	if len(sys.argv) != 4:
		print "herschel_correlations.py lines_file target_data outfile"
	else:
		targ_data = sys.argv[2]
		lines_file = sys.argv[1]
		outfile = sys.argv[3]
		acceptable_types = ["protostar", "Fuor"] #hardcoded for now
		correlations_from_datafile(lines_file, outfile, targ_data, acceptable_types)

	