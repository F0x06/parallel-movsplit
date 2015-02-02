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
import calendar
import datetime
import json
import os
import re
import sys
import time
from cStringIO import StringIO
from datetime import datetime

import exifread
from pycheckjpeg import validate_jpeg_from_buffer

# Function to print debug messages
def ShowMessage(Message, Type=0, Halt=0):

    # Flush stdout
    sys.stdout.flush()

    # Get current date
    DateNow = datetime.now().strftime("%H:%M:%S")

    NO_COLORS = False

    # Display proper message
    Prepend = ""

    if Type == 0:
        if NO_COLORS:
            sys.stdout.write("%s %s[INFO] %s\n" % (DateNow, Prepend, Message))
        else:
            sys.stdout.write("%s \033[32m%s[INFO]\033[39m %s\n" % (DateNow, Prepend, Message))
    elif Type == 1:
        if NO_COLORS:
            sys.stdout.write("%s %s[WARNING] %s\n" % (DateNow, Prepend, Message))
        else:
            sys.stdout.write("%s \033[33m%s[WARNING]\033[39m %s\n" % (DateNow, Prepend, Message))
    elif Type == 2:
        if NO_COLORS:
            sys.stdout.write("%s %s[ERROR] %s\n" % (DateNow, Prepend, Message))
        else:
            sys.stdout.write("%s \033[31m%s[ERROR]\033[39m %s\n" % (DateNow, Prepend, Message))
    elif Type == 3:
        if NO_COLORS:
            sys.stdout.write("%s %s[DEBUG] %s\n" % (DateNow, Prepend, Message))
        else:
            sys.stdout.write("%s \033[34m%s[DEBUG]\033[39m %s\n" % (DateNow, Prepend, Message))

    # Flush stdout
    sys.stdout.flush()

    # Halt program if requested
    if Halt:
        sys.exit()

# Function to find all occurences of a given input
def find_all(a_str, sub):
    start = 0
    while True:
        # Find first element
        start = a_str.find(sub, start)

        # If no match found exit function
        if start == -1: return

        # If there is a match return it and process the next element
        yield start

        # Move pointer to next occurence
        start += len(sub)

# Function to extract JPEG images inside a MOV file
def extractMOV(InputFile, ModuleName, TrashFolder, OutputFolder, Valid_Timestamps):

    # Local variables
    JPEGHeader           = b'\xff\xd8\xff\xe1'

    mov = open(InputFile, 'rb')
    mov_data = mov.read()
    mov.close()

    # Search all JPEG files inside the MOV file
    JPEG_Offsets     = list(find_all(mov_data, JPEGHeader))
    JPEG_Offsets_len = len(JPEG_Offsets)

    # Display message when no headers are found inside the MOV file
    if JPEG_Offsets_len == 0:
        ShowMessage("No JPEG headers found in MOV file %s" % InputFile, 1)

    # Walk over JPEG files positions
    for _Index, _Offset in enumerate(JPEG_Offsets):

        # Calculate the filesize for extraction
        if (_Index >= len(JPEG_Offsets) - 1):
            Size = len(mov_data) - _Offset
        else:
            Size = (JPEG_Offsets[_Index+1] - _Offset)

        # Extract JPEG from MOV file
        ImageData = mov_data[_Offset:(Size + _Offset if Size is not None else None)]

        # Extract EXIF data from JPEG file
        ImageData_File = StringIO(ImageData)
        EXIF_Tags = exifread.process_file(ImageData_File)

        # Output file variables
        timestamp = ""
        Output_Name = ""
        Output_Image = None

        # Calculate the output filename
        date_object = datetime.strptime(str(EXIF_Tags["Image DateTime"]), '%Y:%m:%d %H:%M:%S')
        epoch = calendar.timegm(date_object.utctimetuple())
        timestamp = "%d_%06d" % (epoch, int(str(EXIF_Tags["EXIF SubSecTimeOriginal"])))
        Output_Name = "%d_%s_%s" % (epoch, EXIF_Tags["EXIF SubSecTimeOriginal"], ModuleName)

        # Check if timestamp is valid
        if (timestamp in Valid_Timestamps):

            # Chceck image integrity
            jpeg_messages = validate_jpeg_from_buffer(ImageData)

            # Check presence of error or warning messages
            if jpeg_messages[0] or jpeg_messages[1]:

                # Debug output
                ShowMessage("Image is corrupted (%s).jp4" % Output_Name, 1)

                # Create output trash dir if not exists
                if not os.path.isdir(TrashFolder):
                    os.makedirs(TrashFolder)

                # Open output file
                Output_Image = open('%s/%s.jp4' % (TrashFolder, Output_Name), 'wb')

            else:

                # Create output trash dir if not exists
                if not os.path.isdir(OutputFolder):
                    os.system("mkdir -p %s" % OutputFolder)
                    time.sleep( 1 )

                # Open output file
                Output_Image = open('%s/%s.jp4' % (OutputFolder, Output_Name), 'wb')

        # write the file
        if Output_Image:
            Output_Image.write(ImageData)
            Output_Image.close()

        # Close StringIO image stream
        ImageData_File.close()

# Function to load validated timestamps from CSPS JSON file
def LoadTimestampsFromJSON(JSONFile):

    # Results variable
    Results = []

    # Open file
    SourceJSON = open(JSONFile, 'r')

    # Load JSON file
    json_data = json.load(SourceJSON)

    # Close file
    SourceJSON.close()

    # Get pose sections
    poses = json_data['pose']

    # Iterate over pose sections
    for j in poses:

        # Check if status is unknown
        if j['status'] == 'validated':

            # Append result
            Results.append("%d_%06d" % (j['sec'], j['usc']))

    # Return result
    return sorted(Results)

# Program entry point function
# pylint: disable=W0603
def main(argv):

    # Extract module name  and first timestamp from MOV path
    exp = re.match( r'.*/(\d+)/(\d+)_\d+\.mov', argv[0])

    # Get module name
    Module = int( exp.group(1) )

    # Compute JSON file path
    __JSONFile__ = "%s/info/rawdata-autoseg/segment.json" % (argv[1])

    # Compute corrupted EXIF trashing folder
    __Trash__    = "%s/info/corrupted/jp4" % (argv[1])

    # Load valid timestamps list
    Valid_Timestamps = LoadTimestampsFromJSON(__JSONFile__)

    # Extract MOV file
    extractMOV(argv[0],   # MOV path
               Module,    # Module name
               __Trash__, # Trash folder for corrupted EXIF files
               "%s/jp4/%s" % (argv[1], exp.group(2)[:7]), # Output folder to write JP4 files
               Valid_Timestamps) # List of valid timestamps to be extracted

# Program entry point
if __name__ == "__main__":
    main(sys.argv[1:])
