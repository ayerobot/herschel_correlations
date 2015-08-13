Here's some data mining/plotting tools for looking at Herschel Space Telescope line emissions!

Basic overview: 

First, the herschel_mining.py file computes correlations from the CDF_archive 1d lines files (either SPIRE, PACS, or the merged file I created myself). This produces a large CSV file of line emission pairs. It takes a CDF_archive 1d file and a CSV file with target properties (i.e. type, Lbol, etc ). The target properties file is also used for some other correlations. The list of acceptable types is hardcoded into the python file for now (that can be easily changed before re-running the script). An example of a properties file is included. 

plot_lines.py also reads from the CDF_archive 1d lines file, and produces a scatter plot of one line vs another line with targets labeled. 

The other functions, such as compare_prefixes.py, iterate through the large CSV file to produce subsets matching a specific pattern, such as all pairs where one is a CO line and the other is an OH line. 

CO/13CO vs J plotting is included in the herschel_mining.py, but there's no command-line interface yet. Feel free to import it into another script and use it! 

More detailed documentation forthcoming. 