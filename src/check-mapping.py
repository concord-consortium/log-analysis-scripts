#!/usr/bin/env python3

import shortuuid
import argparse
import csv
import sys
import io

parser = argparse.ArgumentParser(description="De-identify a list of columns from a CSV file.",
                                 epilog="The columns are masked using UUIDs and a separate mapping file is written to map.csv")
parser.add_argument("filename", help="CSV file")
parser.add_argument("-i", "--identifier", action="store", help="Heading of a column to de-identify. Can be specified more than once.")
parser.add_argument("-t", "--to", action="store", help="Heading of a column to de-identify. Can be specified more than once.")
parser.add_argument("-v", "--verbose", action="store_true", help="Print information while running")
parser.add_argument("-o", "--output", required=True, action="store", help="Path to identifier mapping file")

def remove_column(filename, identifier, to):
    id_map = {}
    with open(filename, encoding="utf-8", mode="r") as file:
        csv_reader = csv.reader(file)
        writer = csv.writer(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'), lineterminator='\n')
        
        # Get the header
        header = next(csv_reader)
        col_indexes = []

        try:
            col_indexes.append(header.index(identifier))
            col_indexes.append(header.index(to))
            
        except ValueError:
            sys.stderr.write("Error: Could not find one or more specified columns; columns are: " + ", ".join(header))
            exit(1)
        if (args.verbose):
            sys.stderr.write('Removing column: ' + identifier + '\n')
        id_map[identifier] = {}

        writer.writerow(header)

        rows = 0
        for row in csv_reader:
            rows += 1
            if (args.verbose and rows % 1000 == 0):
                sys.stderr.write(f"Processed {rows} rows\n")
            
            id = row[col_indexes[0]]

            if (id):
                if (id in id_map):
                    continue
                else:
                    id_map[identifier][id] = row[col_indexes[1]]

            writer.writerow(row)
        return id_map
    
def write_mapping_file(filename, map):
    with open(filename, encoding="utf-8", mode="w") as file:
        # Write a CSV file with each key from id_map in the first column and the corresponding value in the second column
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(['original_identifier','masked_identifier','column'])
        for column, mapping in map.items():
            for identifier, mask in mapping.items():
                writer.writerow([identifier, mask, column])

if __name__ == "__main__":
    args = parser.parse_args()
    id_map = remove_column(args.filename, args.identifier, args.to)
    write_mapping_file(args.output, id_map)
