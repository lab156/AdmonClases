#! /bin/bash

source ./course_info

template_file=$1

sed -e "s;%COURSENAME%;$COURSENAME;g" -e "s;%ORDINAL%;$2;g" $1
