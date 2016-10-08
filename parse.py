#! /bin/python

# Import necessary libraries
import os
import glob
import datetime
import re
import sys


# Reads a data file and returns a list of string tuples
# Each tuple consists of a [wavelength, irradiance] data point
# This reads in lines of text that does not start with the '"' or ':' characters
def get_data(filename):

    data = []
    with open(filename) as f:
        for line in f:
            if (line[0][0] != "\"" and line[0][0] != ":"):
                data.append(line.split())
                
    return data
    
# Reads in the name of a file and extracts metadata from it
# Returns a tuple of strings.  If no meaningful pattern is found, the strings are empty
def parse_file(file):
    plot = ''
    subplot = ''
    position = ''
    
    # splits off the timestamp and file extension, leaving only the string before the first '.' character
    psp = file.split('.')[0]    
    
    # disregards filenames with out and approx in them
    if ("out" not in psp and "approx" not in psp):
        # looks for the pattern with one or two digits [0-9][0-9]?, followed by a letter [A-Z],
        # followed by at least one character .+
        # pattern is case-insensitive
        m = re.compile('^([0-9][0-9]?)([A-Z])(.+)', re.IGNORECASE).match(psp)
        if m is not None:
            # groups are based on parenthetical divisions in the search
            plot = m.group(1)
            subplot = m.group(2)
            position = m.group(3)
            
            # custom position rules
            if position == 'atMeristem':
                position = 'M'
            elif position == 'UatMeristem':
                position = 'U'
            elif position == 'inbetween':
                position = 'B'
            elif position == 'SM':
                position = 'S'
            elif position == 'WM':
                position = 'W'
                
        else:
            # if the file does not follow the previous pattern, it looks for 'above' followed by 
            # one or more digits [0-9]+
            m = re.compile('^above([0-9]+)', re.IGNORECASE).match(psp)
            if m is not None:
                plot = m.group(1)
                subplot = 'C'
                position = 'A'            
        
    return [plot, subplot, position]
    
def main(argv):

    names_only = True
    
    # if '--full' is passed in at the command line, then create the huge file
    if len(argv) > 0 and argv[0] == '--full':
        names_only = False
    
    # Set the path and look only for IRR files
    data_set = "data"
    levels = "*/*.IRR"
    
    path = os.path.join(data_set, levels)

    output = "out.csv"
    output_full = "out_full.csv"
    
    # start writing the sample file and the huge output file (if required)
    f = open(output, 'w')
    f.write("Date,Time,Plot,Subplot,Position,Filename\n")    
    if not names_only:
        g = open(output_full, 'w')
        g.write("Date,Time,Plot,Subplot,Position,Wavelength,Irradiance,Filename\n")
    
    # Loop through the files to process (extension selected by wildcard)
    for filename in glob.iglob( path ):

        # get name of file only 
        file = os.path.basename(filename)
        
        # Use statinfo to get a bunch of info about the file
        statinfo = os.stat(filename)

        # Extract only the info on modification time (st_mtime)
        timestamp = statinfo.st_mtime

        # Convert the timestamp to readable date
        date = datetime.datetime.fromtimestamp(timestamp)
        date_str = date.strftime("%Y-%m-%d")
        time_str = date.strftime("%H:%M")

        # get file contents if writing the huge output file
        if not names_only:
            data = get_data(filename)
        
        # parse the file names for metadata
        pf = parse_file(file)
        
        # continue writing to the sample file and the huge file (if necessary)
        f.write("{},{},{},{},{},{}\n".format(date_str, time_str, pf[0], pf[1], pf[2], file))
        if not names_only:
            for datum in data:
                g.write("{},{},{},{},{},{},{},{}\n".format(date_str, time_str, pf[0], pf[1], pf[2], datum[0], datum [1], file))
                
    # close the files, we're done!    
    f.close()
    if not names_only:
        g.close()

if __name__ == "__main__":
    main(sys.argv[1:])
