import sys
import io
import csv
import json
import argparse
import subprocess

parser = argparse.ArgumentParser(description="Process a raw log file using the scripts in this repository",
                                 epilog="The processed CSV file is sent to standard output.")
parser.add_argument("filename", help="CSV file")
parser.add_argument("-v", "--verbose", action="store_true", help="Print progress information while running")

def filter_clue(filename):
    cmd = 'csvgrep -e utf-8 -z 10000000 -c application -m CLUE ' + filename + ' > .\\logs-clue-only.csv'
    subprocess.call(cmd, shell=True)
    if (args.verbose):
       print('Logs filtered to include CLUE records only.')

def expand_parameters(filename):
    cmd = '..\\python.exe .\\src\\expand-json-fields.py -c parameters -f documentUid -f documentKey -f documentType -f documentVisibility -f documentChanges -f commentText -f curriculum -f tileId -f tileType -f objectId -f objectType -f sectionId -f sourceObjectId -f sourceUsername -f sourceDocumentKey -f sourceDocumentType -f sourceSectionId -f serializedObject -f title -f text -f type -f targetUserId -f targetGroupId -f groupId -f studentId -f toolId -f target -f tileTitle -f tab_name -f tab_section_name -f arrowId -f sourceTileId -f sourceTileType -f targetTileId -f targetTileType -f showOrHide -f newTitle -f networkClassHash -f networkUsername -f args -f sourceTile -f sharedTiles -f via -f group .\\logs-clue-only.csv > .\\logs-parameters-expanded.csv'
    subprocess.call(cmd, shell=True)
    if (args.verbose):
       print('Parameters column expanded.')

if __name__ == '__main__':
  args = parser.parse_args()
  filter_clue(args.filename)
  expand_parameters('./logs-clue-only.csv')