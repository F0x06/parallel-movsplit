#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
import json
import sys

# Function to check if a segment is already extracted
def SegmentFinished(JSONFile):

    # Open file
    SourceJSON = open(JSONFile, 'r')

    # Load JSON file
    json_data = json.load(SourceJSON)

    # Close file
    SourceJSON.close()

    # Check if segment is already extracted
    if json_data['split']:
        return True
    else:
        return False

# Program entry point function
# pylint: disable=W0603
def main(argv):

    # Compute JSON file path
    __JSONFile__ = "%s/info/rawdata-autoseg/segment.json" % (argv[0])

    # Return status
    State = SegmentFinished( __JSONFile__ )

    if State:
        sys.exit( 1 )
    else:
        sys.exit( 0 )

# Program entry point
if __name__ == "__main__":
    main(sys.argv[1:])
