import sys
from herschel_correlations import load_data, save_data, swap_lines

#all correlations with a specific line 
#setting line1 of result to the target line, for ease of sorting the final result
def line_correlations(data, targetline, threshold):
	correlations = []
	for cor in data:
		if cor['line1'] == targetline:
			correlations.append(cor)
		elif cor['line2'] == targetline:
			cor2 = swap_lines(cor)
			correlations.append(cor2)
	return correlations


if __name__ == "__main__":
	if len(sys.argv) != 4:
		print "line_correlations.py correlations_file target_line threshold"
	else:
		correlations_file = sys.argv[1]
		target_line = sys.argv[2]
		threshold = float(sys.argv[3])
		data = load_data(correlations_file)
		corr = line_correlations(data, target_line, threshold)
		save_data(corr, target_line + "_correlations" +  ".csv")	
