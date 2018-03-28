#! /usr/bin/env python
# Author: Brendan Ryan
# Date created: 1/31/2018
# Archives Opto log records into folders corresponding to their respective year

import time;

start = time.time()

import os;
import sys;
import glob;
import csv;
import datetime;

# Checks if EOF has been reached
def isLast(itr):
    old = itr.next()
    for new in itr:
        yield False, old
        old = new
    yield True, old

def write_log(fpath, dirpath, log_arr, header_row):
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)

    if os.path.isfile(fpath):
        write_type = "ab"
    else:
        write_type = "wb"

    with open(fpath, write_type) as csv_outfile:
        writer = csv.writer(csv_outfile, dialect='excel')
        if write_type == "wb":
            writer.writerow(header_row)
        for line in log_arr:
            writer.writerow(line)

def process_csv_file(fname):
    row_arr = []
    new_log_arr = []
    prevlogyear = None

    try:
        with open(fname, "rU") as csv_file:
            header_row = ""
            csv_reader = csv.reader((line.replace('\0','') for line in csv_file), quotechar="|")
            include_main_header = True
            
            for idx, (is_last, row) in enumerate(isLast(csv_reader)):
                if not row or row[0] == "":
                    continue 

                if row[0] == "Date":
                    header_row = row
                    continue

                logyear = ""
                current_row = idx + 2

                logdate = row[0]

                logyear = str(logdate)[:4]
                if len(logyear) != 4 or logyear[0] != '2':
                    continue

                if prevlogyear is None:
                    prevlogyear = logyear

                # Create convenience variables for readability
                prevlog_from_current_year = prevlogyear == str(datetime.datetime.now().year)
                log_from_current_year = logyear == str(datetime.datetime.now().year)
                logyear_changed = logyear != prevlogyear
                
                sys.stdout.write("Reading line " + str(current_row) + " of " + fname + "                                 \r")
                sys.stdout.flush()

                if logyear_changed and is_last:
                    if log_from_current_year:
                        write_log(".\\tmp\\new-" + fname, ".\\tmp", [row], header_row)
                    else:
                        write_log(".\\" + logyear + "\\" + fname, logyear, [row], header_row)

                if logyear_changed or is_last or len(row_arr) >= 500000:
                    if prevlog_from_current_year:
                        if is_last and not logyear_changed:
                            new_log_arr.append(row)

                        write_log(".\\tmp\\new-" + fname, ".\\tmp", new_log_arr, header_row)

                        new_log_arr = []
                    else:
                        if is_last and not logyear_changed:
                            row_arr.append(row)

                        write_log(".\\" + prevlogyear + "\\" + fname, prevlogyear, row_arr, header_row)

                        row_arr = []
                        
                    prevlogyear = logyear

                if log_from_current_year:
                    new_log_arr.append(row)
                else:
                    row_arr.append(row)

    except UnicodeDecodeError:
        print "Malformed CSV: " + fname

    os.remove(fname)
    if os.path.isfile(".\\tmp\\new-" + fname):
        os.rename(".\\tmp\\new-" + fname, ".\\" + fname)

def main():
    dir_array = ["C:\\Users\\Brendan Ryan\\Desktop\\OptoLogs\\BNA", "C:\\Users\\Brendan Ryan\\Desktop\\OptoLogs\\Dept3",
                 "C:\\Users\\Brendan Ryan\\Desktop\\OptoLogs\\Dept5", "C:\\Users\\Brendan Ryan\\Desktop\\OptoLogs\\Foreman",
                 "C:\\Users\\Brendan Ryan\\Desktop\\OptoLogs\\Ovens", "C:\\Users\\Brendan Ryan\\Desktop\\OptoLogs\\Robot",
                 "C:\\Users\\Brendan Ryan\\Desktop\\OptoLogs\\Waste Water"]

    for dname in dir_array:

        print "Reading log files in " + dname + "..."

        os.chdir(dname)

        for fname in glob.glob("*.csv"):
            process_csv_file(fname)

        # Delete tmp folder created by process_csv_file
        if os.path.isdir(".\\tmp"): 
            os.rmdir(".\\tmp")

    print "                                         \r"
    print "Done."

main()

finish = time.time()

print "Time: " + str(finish - start)