#command-line utility for comparing different lines from Herschel data, 
#i.e. lines that both start with differnt prefixes
#this requires all correlations to have been already computed, in herschel_correlations.py
import sys
from herschel_correlations import load_data, save_data, swap_lines

#find all correlations between lines starting with prefix 1 and prefix 2
#re-arranging lines so that prefix1 is in first line column, prefix2
def compare_prefixes(data, prefix1, prefix2, threshold):
	correlations = []
	for cor in data:
		if cor['line1'].startswith(prefix1) and cor['line2'].startswith(prefix2):
			correlations.append(cor)
		elif cor['line2'].startswith(prefix1) and cor['line1'].startswith(prefix2):
			correlations.append(swap_lines(cor))
	return correlations

if __name__ == "__main__":
	if len(sys.argv) != 5:
		print "compare_prefixes.py correlations_file prefix1 prefix2 threshold"
	else:
		correlations_file = sys.argv[1]
		prefix1 = sys.argv[2]
		prefix2 = sys.argv[3]
		threshold = float(sys.argv[4])
		data = load_data(correlations_file)
		corr = compare_prefixes(data, prefix1, prefix2, threshold)
		save_data(corr, prefix1 + "_" + prefix2 +  ".csv")	
