#!/bin/bash

# Script parameters #
PARAM_MOUNT="/data/"
PARAM_MAC=""
PARAM_MASTER=""
PARAM_SEGMENT=""

# Arguments and parameters parser #
arguments() {

    # Search in arguments #
    while [[ $# > 0 ]]; do

        args="$1"
        shift
        case $args in
            --no-split)
                echo --no-split given exiting...
                exit
            ;;
            --mount-point)
                PARAM_MOUNT="$1"
                shift
            ;;
            --mac-address)
                PARAM_MAC="$1"
                shift
            ;;
            --master-timestamp)
                PARAM_MASTER="$1"
                shift
            ;;
            --segment-timestamp)
                PARAM_SEGMENT="$1"
                shift
            ;;
        esac

    done

}

# Argument and parameters #
arguments $@

# Check execution consistency #
if [ ! -d $PARAM_MOUNT/camera ] || [ ! -d $PARAM_MOUNT/footage ]; then

    # Exit script #
    echo "Error : unable to access standard directory with specified mount point"
    exit 1

fi

# Check execution consistency #
if [ -z "$PARAM_MAC" ] || [ -z "$PARAM_MASTER" ]; then

    # Exit script #
    echo "Error : cannot continue execution without --mac-address/--master-timestamp parameters"
    exit 1

fi

# SSH configs cirectory
SSH_CONFIGS_DIR="$PARAM_MOUNT/ssh-configs/rawdata-procedures"

# SSH config file
SSH_CONFIG_FILE="$SSH_CONFIGS_DIR/rawdata-movsplit.conf"

# Segments base folder
SEGMENTS_DIR="$PARAM_MOUNT/camera/$PARAM_MAC/raw/segment/$PARAM_MASTER"

# Splitting script
SPLIT_SCRIPT="scripts/rawdata-movsplit-splitter.py"

# JSON updater script
JSONUPDATE_SCRIPT="scripts/rawdata-movsplit-jsonupdater.py"

# State script
STATE_SCRIPT="scripts/rawdata-movsplit-state.py"

# Check if a segment is specified
if [ -z "$PARAM_SEGMENT" ]; then

    # Iterate over segments
    for d in $SEGMENTS_DIR/* ; do

        # Determine segment folder
        SEGMENT_TIMESTAMP=$(basename $d)
        SEGMENT_FOLDER=$SEGMENTS_DIR/$SEGMENT_TIMESTAMP

        # Check if segment is already splitted
        python $STATE_SCRIPT $SEGMENT_FOLDER
        if [ $? -eq 1 ]; then
            echo "Segment $SEGMENT_TIMESTAMP already splitted, skipping"
        else

            # Split segment
            echo Splitting segment $d...
            echo find $SEGMENT_FOLDER/mov -iname '*.mov' | sort | parallel --eta --ungroup --sshloginfile $SSH_CONFIG_FILE --bf $SPLIT_SCRIPT python $SPLIT_SCRIPT {} $SEGMENT_FOLDER

            # Update JSON file
            echo Updating segment JSON file...
            echo python $JSONUPDATE_SCRIPT $SEGMENT_FOLDER
        fi
    done

else

    # Determine segment folder
    SEGMENT_FOLDER=$SEGMENTS_DIR/$PARAM_SEGMENT

    # Check if segment is already splitted
    python $STATE_SCRIPT $SEGMENT_FOLDER
    if [ $? -eq 1 ]; then
        echo "Segment $PARAM_SEGMENT already splitted, skipping"
    else

        # Split segment
        echo Splitting segment $PARAM_SEGMENT...
        find $SEGMENT_FOLDER/mov -iname '*.mov' | sort | parallel --eta --ungroup --sshloginfile $SSH_CONFIG_FILE --bf $SPLIT_SCRIPT python $SPLIT_SCRIPT {} $SEGMENT_FOLDER

        # Update JSON file
        echo Updating segment JSON file...
        python $JSONUPDATE_SCRIPT $SEGMENT_FOLDER
    fi

fi
