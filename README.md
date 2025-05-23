# Log Analysis Scripts

This is a collection of Python scripts that work with log files of the sort generated by Concord Consortium tools.

## Prerequisites

Python 3 is assumed.

## Installation

Clone this repository and `cd` into its directory.

Recommended:  create a [virtual environment](https://docs.python.org/3/library/venv.html) for python:

```shell
python3 -m venv venv
source venv/bin/activate
```

The first line is one-time setup; the second "source" command must be repeated each time you open a new terminal window. You should see "venv" in your prompt when the virtual environment is activated.

Install the required Python packages:

```shell
pip install -r requirements.txt
```

## Scripts included

For all scripts:

- `cd` to the application directory
- Make sure the virtual environment has been activated (`source venv/bin/activate`, as above)

Command line argument `-v` or `--verbose` will print out additional information.

Command line argument `-h` or `--help` will show all available command line options and usage information.

### `check-date-range.py`

**Shows the distribution of dates in a 'timestamp' column of a CSV.**

Our log files CSVs have timestamp columns that use seconds or milliseconds since the 'Unix epoch' (Jan 1 1970).
This script reads these and shows you the range of dates included in the file in an easily readable way.

```shell
./src/check-date-range.py log-file.csv
```

Will output something like this, showing the number of lines with timestamps in each month:

```text
Earliest date: 2021-11-05 12:32:04
Latest date:   2022-06-06 10:11:10.106000
2021-11:     248 ########
2021-12:      85 ###
2022-01:     700 #####################
2022-02:      94 ###
2022-03:      75 ###
2022-04:     281 #########
2022-05:      80 ###
2022-06:       7 #
```

### `split-by-date.py`

**Split CSV file into one-year chunks using a timestamp column.**

If you have a sorted, multi-year log file, this will split it into chunks with one year of data in each.  You can specify which month to use as the split point; eg if you want school years or fiscal years rather than calendar years.

The following command line will split `giant-file.csv` into files named `yearly-file-2021.csv`, `yearly-file-2022.csv`, etc.  Since we've chosen month 8, the 2021 file will contains dates from Aug 1, 2021 through July 31, 2022.

```shell
./src/split-by-date.py --month 8 -c timestamp -o yearly-file- giant-file.csv
```

### `analyze-json-column.py`

**Analyzes columns of a CSV log file that contain JSON data, and lists all of the keys that occur in the JSON.**

You must supply the name of the CSV file and the heading of the column that contains the JSON data (generally `parameters` or `extras` for CC logs), eg

```shell
./src/analyze-json-column.py -c parameters my-data-file.csv
```

The output will be a list of keys, one per line, using dots to separate levels of hierarchy.  
So if the JSON data only included:

```json
{ "role": "student",
  "page": { "number": 1, "title: "Introduction" } }
```

The output would be:

```text
role
page.number
page.title
```

This is mostly useful so that you know what keys can be used with the next script.

### `expand-json-fields.py`

**Extract fields from a JSON column of a CSV file into their own columns.**

You supply the heading of JSON column and one or more fields that exist in that column (dot-separated, as above), and this script will extract the values of those fields in each row to their own columns.
These columns will be added after all existing columns.
The JSON column will be removed.

Example:

```shell
./src/expand-json-fields.py -c parameters -f problem -f role my-data-file.csv > new-file.csv
```

### `deidentify-columns.py`

**Replace the values in one or more columns with opaque identifiers.**

You specify the names of one or more columns (eg, `student name`), and each unique value will be replaced with an anonymous identifier
(specifically, this is a short uuid built from the original value).

A file is also written out with the mapping of original values to hashed values.

Example:

```shell
./src/deidentify-columns.py -c student_name -c school -m mapping.csv my-data-file.csv > new-file.csv
```

### `process-teacher-column.py`

**Extract teacher usernumbers from the teacher column and create a mapping file.**

You supply the path to the student data file, and this script will extract teacher usernumbers from the teacher column to their own column.
The column will be added after all existing columns.
The teacher column will be removed and a mapping file relating teacher names to teacher usernumbers will be generated.

Example:

```shell
./src/process-teacher-column.py student-log-file.csv -m mapping-file.csv > new-student-log-file.csv
```

## License

All content is (c) [The Concord Consortium](https://concord.org) and licensed under the [MIT License](LICENSE).
