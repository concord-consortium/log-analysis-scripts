#!/usr/bin/env python3

import shortuuid
import argparse
import csv
import sys
import io

parser = argparse.ArgumentParser(description="De-identify a list of columns from a CSV file.",
                                 epilog="The columns are masked using UUIDs and a separate mapping file is written to map.csv")
parser.add_argument("filename", help="CSV file")
parser.add_argument("-c", "--column", action="append", help="Heading of a column to de-identify. Can be specified more than once.")
parser.add_argument("-v", "--verbose", action="store_true", help="Print information while running")
parser.add_argument("-m", "--mapfile", required=True, action="store", help="Path to identifier mapping file")

def deidentify_fields(filename, columns):
    id_map = {}
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
                    # Use the value stored in id_map if there is one; otherwise generate a new masked value
                    if (data in id_map):
                        mask = id_map[data]
                    else:
                        mask = shortuuid.uuid(name=data)
                        id_map[data] = mask
                    row[col_index] = mask

            writer.writerow(row)
        return id_map
    
def write_mapping_file(filename, map):
    with open(filename, encoding="utf-8", mode="w") as file:
        # Write a CSV file with each key from id_map in the first column and the corresponding value in the second column
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(['original_identifier','masked_identifier'])
        for key, value in map.items():
            writer.writerow([key, value])

if __name__ == "__main__":
    args = parser.parse_args()
    id_map = deidentify_fields(args.filename, args.column)
    write_mapping_file(args.mapfile, id_map)
