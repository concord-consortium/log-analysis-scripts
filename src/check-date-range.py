#!/usr/bin/env python3

import datetime
import sys
import csv
import argparse

parser = argparse.ArgumentParser(description="Show the dates included in a timestamp column of a CSV file.",
                                 epilog="Either unix-style timestamps or milliseconds since the epoch are accepted.")
parser.add_argument("filename", help="CSV file")
parser.add_argument("-c", "--column", default="timestamp", help="Heading of the column containing timestamp data")
parser.add_argument("-v", "--verbose", action="store_true", help="Print information while running")

# Some log files have very long data in the columns
csv.field_size_limit(10000000)

def parse_file(filename, timestamp_field):
  non_numeric = 0
  earliest = None
  latest = None
  months = {}
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
          non_numeric += 1
          continue
        if (timestamp):
          if (timestamp > 10000000000):
            # Must be formatted in milliseconds
            timestamp = timestamp / 1000
          date = datetime.datetime.fromtimestamp(timestamp)
          if (earliest is None or date < earliest):
            earliest = date
          if (latest is None or date > latest):
            latest = date
          month = date.strftime("%Y-%m")
          if month not in months:
            months[month] = 0
          months[month] += 1
  if non_numeric > 0:
    sys.stderr.write("Non-numeric values found: " + str(non_numeric) + "\n")
  return earliest, latest, months


if __name__ == '__main__':
  args = parser.parse_args()
  earliest, latest, months = parse_file(args.filename, args.column)
  if (len(months) == 0):
    sys.stderr.write("No dates found\n")
    exit(1)
  print(f"Earliest date: {earliest}")
  print(f"Latest date:   {latest}")
  # Show the number of entries per month
  # Print 1 to 20 '#' characters to show the relative sizes of the numbers.
  max_count = max(months.values())
  for month in sorted(months.keys()):
    count = months[month]
    bar_length = int((count / max_count) * 20)+1
    bar = '#' * bar_length
    print(f"{month}: {count:7d} {bar}")
