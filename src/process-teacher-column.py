#!/usr/bin/env python3

import argparse
import csv
import sys
import io
import re

csv.field_size_limit(sys.maxsize)
parser = argparse.ArgumentParser(description="Process the teachers column",
                                 epilog="Retains primary teacher user ID and removes names")
parser.add_argument("filename", help="CSV file")
parser.add_argument("-v", "--verbose", action="store_true", help="Print information while running")
parser.add_argument("-m", "--mapfile", required=True, action="store", help="Path to identifier mapping file")

def process_column(filename):
    id_map = {}
    with open(filename, encoding="utf-8", mode="r") as file:
        csv_reader = csv.reader(file)
        writer = csv.writer(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'), lineterminator='\n')
        
        # Get the header
        header = next(csv_reader)
        
        try:
            col_index = header.index('teachers')
        except ValueError:
            sys.stderr.write("Error: Could not find teachers column; columns are: " + ", ".join(header))
            exit(1)
        if (args.verbose):
            sys.stderr.write('Processing teacher column...\n')
        id_map['teacher'] = {}
        header.append('teacher')
        writer.writerow(header)

        rows = 0
        for row in csv_reader:
            rows += 1
            if (args.verbose and rows % 1000 == 0):
                sys.stderr.write(f"Processed {rows} rows\n")
        
            data = row[col_index]
            teacher = re.search("\w+\s\w+", data).group()

            if (data):
                # Use the value stored in id_map if there is one; otherwise generate a new masked value
                if (teacher in id_map):
                    mask = id_map[header[col_index]][data]
                else:
                    mask = re.search("\d+", data).group()
                    id_map['teacher'][teacher] = mask
                row[col_index] = mask
                row.append(mask)

            writer.writerow(row)
        return id_map
    
def write_mapping_file(filename, map):
    with open(filename, encoding="utf-8", mode="w") as file:
        # Write a CSV file with each key from id_map in the first column and the corresponding value in the second column
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(['teacher_name','id'])
        for column, mapping in map.items():
            for identifier, mask in mapping.items():
                writer.writerow([identifier, mask])

if __name__ == "__main__":
    args = parser.parse_args()
    id_map = process_column(args.filename)
    write_mapping_file(args.mapfile, id_map)
