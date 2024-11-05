import sys
import io
import csv
import json
import argparse
import subprocess

parser = argparse.ArgumentParser(description="Process a raw log file using the scripts in this repository",
                                 epilog="The processed CSV file is sent to standard output.")
parser.add_argument("filename", help="CSV file")
parser.add_argument("-v", "--verbose", action="store_true", help="Print progress information while running")

def process_file(filename):
    cmd = 'csvgrep -z 10000000 -c application -m CLUE ' + filename + ' > .\logs-clue-only.csv'
    subprocess.call(cmd, shell=True)
    if (args.verbose):
       print('Logs filtered to include CLUE records only.')

if __name__ == '__main__':
  args = parser.parse_args()
  process_file(args.filename)