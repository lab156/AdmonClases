#! /bin/bash

source course_info

template_file=$1

sed -e "s;%COURSENAME%;$COURSENAME;g"\
    -e "s;%COURSECODE%;$COURSECODE;g"\
    -e "s;%COURSEINSTRUCTOR%;$COURSEINSTRUCTOR;g"\
    -e "s;%COURSESEMESTER%;$COURSESEMESTER;g"\
    -e "s;%ORDINAL%;$2;g" $template_file  
