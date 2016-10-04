#! /bin/bash

CLASE_RAIZ=../..
cd $CLASE_RAIZ

#Hacemos un symbolic link de create_new_lecture.sh
ln -s AdmonClases/create_new_lecture.sh .

#Copiamos el archivo de la informacion de la clase
cp AdmonClases/templates/course_info_default course_info

#Copiamos el archivo de gitignore
cp AdmonClases/templates/git_ignore_default .gitignore

#Copiamos el archivo de vimdir
cp AdmonClases/templates/vim_dir .vimdir

#Link email_it to run it from Course Root dir
ln -s AdmonClases/scripts/email_it.py .

#Copiamos el archivo de opciones para el correo
cp AdmonClases/templates/config_correo_py_template config_correo.py
