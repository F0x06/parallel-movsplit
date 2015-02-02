#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  rawdata-procedures - Camera raw data procedures

  Copyright (c) 2013-2015 FOXEL SA - http://foxel.ch
  Please read <http://foxel.ch/license> for more information.


  Author(s):

       Kevin Velickovic <k.velickovic@foxel.ch>


  This file is part of the FOXEL project <http://foxel.ch>.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.


  Additional Terms:

       You are required to preserve legal notices and author attributions in
       that material or in the Appropriate Legal Notices displayed by works
       containing it.

       You are required to attribute the work as explained in the "Usage and
       Attribution" section of <http://foxel.ch/license>.
"""

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
