#!/bin/bash

python AdmonClases/scripts/email_it.py mens_tareas.txt \
         --listado Listado.ods \
         --subject "Tarea" \
         --correos "Correo Institucional" "Correo Personal" \
         --attach "tarea8"\
         #--hoysi \
         #--exanum Total \
         #--hist 
         
