#!/usr/bin/env python3

import sys
import csv
import json
import argparse

parser = argparse.ArgumentParser(description="Extract a list of fields from a JSON column of a CSV file.",
                                 epilog="The fields are output in a sorted list, one per line, with dots separating nested fields.")
parser.add_argument("filename", help="CSV file")
parser.add_argument("-c", "--column", default="parameters", help="Heading of the column containing JSON data")
parser.add_argument("-v", "--verbose", action="store_true", help="Print information while running")

# Skip any descendants of these keys
skip_values_of = ["serializedObject"]

# Some log files have very long data in the columns
csv.field_size_limit(10000000)

def find_fields(data: any, fields, prefix: str = ""):
  for key in data:
    if isinstance(data[key], dict) and not (key in skip_values_of):
      find_fields(data[key], fields, prefix + key + ".")
    else:
      if prefix + key not in fields:
          if args.verbose:
            sys.stderr.write(f"Found field: {prefix + key}\n")
          fields.append(prefix + key)

def parse_file(filename, json_field):
  fields = []
  # Read file line-by-line as a CSV
  with open(filename, encoding="utf-8", mode="r") as file:
      csv_reader = csv.reader(file)
      # Get the header
      header = next(csv_reader)
      try:
        param_index = header.index(json_field)
      except ValueError:
        sys.stderr.write("Error: Could not find " + json_field + " column; columns are: " + ", ".join(header))
        exit(1)

      rows = 0
      for row in csv_reader:
        rows += 1
        if (args.verbose and rows % 1000 == 0):
          sys.stderr.write(f"Processed {rows} rows\n")
        json_data = row[param_index]
        if (json_data):
          data = json.loads(json_data)
          find_fields(data, fields)
  return fields


if __name__ == '__main__':
  args = parser.parse_args()
  fields = parse_file(args.filename, args.column)
  fields.sort()
  print("\n".join(fields))
