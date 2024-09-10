#!/usr/bin/env python3

import sys
import csv
import json
import argparse

parser = argparse.ArgumentParser(description="Extract fields from a JSON column of a CSV file into their own columns",
                                 epilog="The modified CSV file (with JSON field removed and expanded columns included at the end) is sent to standard output.")
parser.add_argument("filename", help="CSV file")
parser.add_argument("-c", "--column", default="parameters", help="Heading of the column containing JSON data (default: 'parameters')")
parser.add_argument("-f", "--field", required=True, action='append', help="Field(s) to extract. Nested fields should be named with dots separating the levels. " +
          "This argument can be repeated to extract multiple fields.")
parser.add_argument("-v", "--verbose", action="store_true", help="Print progress information while running")

# Some log files have very long data in the columns
csv.field_size_limit(10000000)

# Get a field (provided as a list of keys) from a JSON object
def get_from_json(data, field):
  for component in field:
    if component in data:
      data = data[component]
    else:
      return None
  return data

def process_file(filename, json_column, fields):
  # Split fields on periods to make a list of components
  field_components = [f.split(".") for f in fields]
  # Read file line-by-line as a CSV
  with open(filename, "r") as file:
      csv_reader = csv.reader(file)
      writer = csv.writer(sys.stdout)
      # Get the header
      header = next(csv_reader)
      try:
        param_index = header.index(json_column)
      except ValueError:
        sys.stderr.write("Error: Could not find " + json_column + " column; columns are: " + ", ".join(header))
        exit(1)
      # Remove the JSON column from the header and add columns for the new fields
      header.remove(json_column)
      for f in fields:
        header.append(f)
      writer.writerow(header)

      rows = 0
      for row in csv_reader:
        rows += 1
        if (args.verbose and rows % 1000 == 0):
          sys.stderr.write(f"Processed {rows} rows\n")
        json_data = row[param_index]
        row.pop(param_index)
        if (json_data):
          data = json.loads(json_data)
          for field in field_components:
            row.append(get_from_json(data, field))
        else:
          for field in field_components:
            row.append(None)
        writer.writerow(row)

if __name__ == '__main__':
  args = parser.parse_args()
  process_file(args.filename, args.column, args.field)
