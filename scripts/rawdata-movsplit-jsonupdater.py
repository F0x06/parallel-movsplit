#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
import glob
import json
import os
import re
import sys


def updateJson(JSONFile, CorruptedPath):

    # Local corrupted timestamps container
    TimeStamps = []

    # Iterate over corrupted files
    for filePath in glob.glob("%s/*.jp4" % CorruptedPath):

        # Get file name
        FileName = os.path.basename( filePath )

        # Extract timestamp from file name
        exp = re.match( r'(\d+)_(\d+)_(\d+)\.jp4', FileName)

        # Extract timestamp from JP4 path
        TimeStamp = "%s_%s" % (exp.group(1), exp.group(2))

        # Append timestamp to list
        TimeStamps.append( TimeStamp )

    # Open file
    SourceJSON = open(JSONFile, 'r')

    # Load JSON file
    json_data = json.load(SourceJSON)

    # Close JSON file
    SourceJSON.close()

    # Set 'split' tag to true
    json_data['split'] = True

    # Get pose sections
    poses = json_data['pose']

    # Iterate over poses
    for pose in poses:

        # Compute timestamp
        timestamp = "%d_%06d" % (pose['sec'], pose['usc'])

        # Assing corrupted tag if image is corrupted
        if timestamp in TimeStamps:
            pose['status'] = "corrupted"

    # Write validated JSON file
    with open(JSONFile, 'w') as outfile:
        json.dump(json_data, outfile, sort_keys = True, indent = 4)

# Program entry point function
# pylint: disable=W0603
def main(argv):

    # Compute JSON file path
    __JSONFile__ = "%s/info/rawdata-autoseg/segment.json" % (argv[0])

    # Compute currupted images path
    __CorruptedPath__ = "%s/info/corrupted/jp4" % (argv[0])

    # Tag corrupted images in json
    updateJson( __JSONFile__, __CorruptedPath__)

# Program entry point
if __name__ == "__main__":
    main(sys.argv[1:])
