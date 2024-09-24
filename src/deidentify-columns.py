#!/usr/bin/env python3

import shortuuid
from tqdm import tqdm
import argparse
import csv
import sys

parser = argparse.ArgumentParser(description="De-identify a list of columns from a CSV file.",
                                 epilog="The columns are masked using UUIDs and a separate mapping file is written to map.csv")
parser.add_argument("filename", help="CSV file")
parser.add_argument("-f", "--fields", default="[student_name, school]", help="Array of fields to de-identify")
parser.add_argument("-v", "--verbose", action="store_true", help="Print information while running")

def deidentify_fields(filename, fields):
    with open(filename, "r") as file:
        csv_reader = csv.reader(file)
        writer = csv.writer(sys.stdout)
        
        # Get the header
        header = next(csv_reader)

        for field in tqdm(fields, desc="De-identifying fields..."):
            try:
                field_index = header.index(field)
            except ValueError:
                sys.stderr.write("Error: Could not find " + field + " column; columns are: " + ", ".join(header))
                exit(1) 
            if (args.verbose):
                print('De-identifying column: ' + field)
            rows = 0
            for row in csv_reader:
                rows += 1
                if (args.verbose and rows % 1000 == 0):
                    sys.stderr.write(f"Processed {rows} rows\n")
                
                data = row[field_index]
                row.pop(field_index)
                
                if (data):
                    mask = shortuuid.uuid(name=data)
                    row.append(mask)
                else:
                    row.append(None)
                writer.writerow(row)

if __name__ == "__main__":
    print('Hit main')
    args = parser.parse_args()
    deidentify_fields(args.filename, args.fields)
