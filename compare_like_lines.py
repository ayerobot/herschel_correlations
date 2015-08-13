#command-line utility for comparing like lines from Herschel data, 
#i.e. lines that both start with the same prefix
#this requires all correlations to have been already computed, in herschel_correlations.py
import sys
import numpy as np
from herschel_correlations import load_data, save_data


#syntax: correlations file, the prefix, then the cutoff threshold 
#(i.e. if you only care about things with a correlation above 0.9)
#gets correlations of similar lines against each other (i.e. CO vs other CO lines)
#just iterating through data file
def compare_like_lines(data, prefix, threshold):
	correlations = []
	for cor in data:
		if cor['line1'].startswith(prefix) and cor['line2'].startswith(prefix) and np.abs(cor['r']) > threshold:
			correlations.append(cor)
	return correlations

if __name__ == "__main__":
	if len(sys.argv) != 4:
		print "compare_like_lines.py correlations_file prefix threshold"
	else:
		correlations_file = sys.argv[1]
		prefix = sys.argv[2]
		threshold = float(sys.argv[3])
		data = load_data(correlations_file)
		corr = compare_like_lines(data, prefix, threshold)
		save_data(corr, prefix + "_lines.csv")

