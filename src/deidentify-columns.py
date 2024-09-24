#!/usr/bin/env python3

import shortuuid
import argparse
import csv
import sys

parser = argparse.ArgumentParser(description="De-identify a list of columns from a CSV file.",
                                 epilog="The columns are masked using UUIDs and a separate mapping file is written to map.csv")
parser.add_argument("filename", help="CSV file")
parser.add_argument("-c", "--column", action="append", help="Heading of a column to de-identify. Can be specified more than once.")
parser.add_argument("-v", "--verbose", action="store_true", help="Print information while running")

def deidentify_fields(filename, columns):
    with open(filename, "r") as file:
        csv_reader = csv.reader(file)
        writer = csv.writer(sys.stdout)
        
        # Get the header
        header = next(csv_reader)

        col_indexes = []

        for col in columns:
            try:
                col_indexes.append(header.index(col))
            except ValueError:
                sys.stderr.write("Error: Could not find " + col + " column; columns are: " + ", ".join(header))
                exit(1)
            if (args.verbose):
                sys.stderr.write('De-identifying column: ' + col + '\n')

        rows = 0
        for row in csv_reader:
            rows += 1
            if (args.verbose and rows % 1000 == 0):
                sys.stderr.write(f"Processed {rows} rows\n")
            
            for col_index in col_indexes:
                data = row[col_index]
            
                if (data):
                    mask = shortuuid.uuid(name=data)
                    row[col_index] = mask

            writer.writerow(row)

if __name__ == "__main__":
    args = parser.parse_args()
    deidentify_fields(args.filename, args.column)
