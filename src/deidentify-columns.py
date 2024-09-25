#!/usr/bin/env python3

import shortuuid
import argparse
import csv
import sys
import io
import pandas as pd

parser = argparse.ArgumentParser(description="De-identify a list of columns from a CSV file.",
                                 epilog="The columns are masked using UUIDs and a separate mapping file is written to map.csv")
parser.add_argument("filename", help="CSV file")
parser.add_argument("-c", "--column", action="append", help="Heading of a column to de-identify. Can be specified more than once.")
parser.add_argument("-v", "--verbose", action="store_true", help="Print information while running")
parser.add_argument("-m", "--mapfile", action="store", help="Path to identifier mapping file")

def deidentify_fields(filename, columns, id_map):
    with open(filename, encoding="utf-8", mode="r") as file:
        csv_reader = csv.reader(file)
        writer = csv.writer(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'), lineterminator='\n')
        
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
        
        writer.writerow(header)

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
                    if data in id_map[rows - 1].values():
                        continue
                    else:
                        id_map[rows - 1]['original_identifier'] = data
                        id_map[rows - 1]['masked_identifier'] = mask

            writer.writerow(row)
            return id_map

if __name__ == "__main__":
    args = parser.parse_args()
    id_map = [{}]
    id_map = deidentify_fields(args.filename, args.column, id_map)
    with open(args.mapfile, encoding="utf-8", mode="w") as file:
        writer = csv.DictWriter(sys.stderr, fieldnames = ['original_identifier','masked_identifier'],lineterminator='\n')
        writer.writeheader()
        writer.writerows(id_map)