#!/usr/bin/env python3

import datetime
import sys
import csv
import argparse
import io

parser = argparse.ArgumentParser(description="Divide a CSV file into segments based on a timestamp column.",
                                 epilog="The file must already be sorted by the indicated column (you can use csvsort from csvkit for this).\n"
                                 + "Either unix-style timestamps or milliseconds since the epoch are accepted.")
parser.add_argument("filename", help="CSV file")
parser.add_argument("-c", "--column", default="timestamp", help="Heading of the column containing timestamp data")
parser.add_argument("-o", "--output", required=True, help="Prefix for output files")
parser.add_argument("-m", "--month", default=1, type=int, help="Month that the year is considered to begin, as a number; default is 1 (January)")
parser.add_argument("-v", "--verbose", action="store_true", help="Print information while running")

# Some log files have very long data in the columns
csv.field_size_limit(10000000)

def csv_writer_for_year(output_stem, year):
  filename = f"{output_stem}-{year}.csv"
  if (args.verbose):
    sys.stderr.write(f"Creating {filename}\n")
  # Create file and open in utf-8 text mode
  file = io.open(filename, "w", newline='', encoding='utf-8')
  writer = csv.writer(file, lineterminator='\n')
  return writer

def year_for_date(date, start_month):
  year = date.year
  if date.month < start_month:
    year -= 1
  return year

def parse_file(filename, timestamp_field, output_stem, start_month):
  current_year = None
  non_numeric = 0
  writer = None
  # Read file line-by-line as a CSV
  with open(filename, encoding="utf-8", mode="r") as file:
      csv_reader = csv.reader(file)
      # Get the header
      header = next(csv_reader)
      try:
        col_index = header.index(timestamp_field)
      except ValueError:
        sys.stderr.write("Error: Could not find " + timestamp_field + " column; columns are: " + ", ".join(header))
        exit(1)

      rows = 0
      for row in csv_reader:
        rows += 1
        if (args.verbose and rows % 1000 == 0):
          sys.stderr.write(f"Processed {rows} rows\n")
        try:
          timestamp = int(row[col_index])
        except ValueError:
          if (args.verbose):
            sys.stderr.write(f"Non-numeric timestamp in row {rows}: {row[col_index]}\n")
          non_numeric += 1
          continue
        if (timestamp):
          if (timestamp > 10000000000):
            # Must be formatted in milliseconds
            timestamp = timestamp / 1000
          date = datetime.datetime.fromtimestamp(timestamp)
          year = year_for_date(date, start_month)
          if year != current_year:
            # if writer:
            #   writer.close()
            current_year = year
            writer = csv_writer_for_year(output_stem, year)
            writer.writerow(header)
          writer.writerow(row)

  if non_numeric > 0:
    sys.stderr.write("Rows with non-numeric timestamps skipped: " + str(non_numeric) + "\n")


if __name__ == '__main__':
  args = parser.parse_args()
  parse_file(args.filename, args.column, args.output, args.month)
