#!/bin/bash
#This script normally will be called from the inside of a directory
#this means the course_info file would be one directory above
source ../course_info
if [ -n "$SYNCTOSERVER" ]; then
    echo "......syncing.......";
    cp this_paper.pdf /srv/http/this_paper.pdf ;
else
    echo "...NO SYNC WILL BE DONE...";
fi
