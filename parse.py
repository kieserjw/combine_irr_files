#! /bin/python

# Import necessary libraries
import os
import glob
import datetime
import re
import sys

def get_data(filename):

    data = []
    with open(filename) as f:
        for line in f:
            if (line[0][0] != "\"" and line[0][0] != ":"):
                data.append(line.split())
                
    return data
    
    
def parse_file(file):
    plot = ''
    subplot = ''
    position = ''
    
    psp = file.split('.')[0]    
    if ("out" not in psp and "approx" not in psp):
        
        m = re.compile('^([0-9][0-9]?)([A-Z])(.+)', re.IGNORECASE).match(psp)
        if m is not None:
            plot = m.group(1)
            subplot = m.group(2)
            position = m.group(3)
            
            '''m = re.compile('^([A-Z])atMeristem', re.IGNORECASE).match(position)
            if m is not None:
                position = m.group(1)
            '''
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
            m = re.compile('^above([0-9]+)', re.IGNORECASE).match(psp)
            if m is not None:
                plot = m.group(1)
                subplot = 'C'
                position = 'A'            
        
    return [plot, subplot, position]
    
def main(argv):

    names_only = True
    
    if len(argv) > 0 and argv[0] == '--full':
        names_only = False
    
    # Set the path
    path = "./spring-data/"
    levels = "*/*.IRR"
    path = path + levels

    output = "out.csv"
    output_full = "out_full.csv"

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

        # get file contents
        if not names_only:
            data = get_data(filename)
        
        pf = parse_file(file)
        
        f.write("{},{},{},{},{},{}\n".format(date_str, time_str, pf[0], pf[1], pf[2], file))
        # Print name and date, tab separated
        # print file,'\t',date_str,'\t',time_str
        if not names_only:
            for datum in data:
                g.write("{},{},{},{},{},{},{},{}\n".format(date_str, time_str, pf[0], pf[1], pf[2], datum[0], datum [1], file))
                
        
    f.close()
    if not names_only:
        g.close()

if __name__ == "__main__":
    main(sys.argv[1:])
