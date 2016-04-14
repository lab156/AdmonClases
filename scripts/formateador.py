#! /usr/bin/python3
import subprocess
import sys
import os
from lector_notas import LectorNotasCSV

#Get the path to the main dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

subprocess.call(["unoconv", "-f", "csv", "-e", "FilterOptions=44,34,76", "-o", "/tmp/listado.csv", "%s"%os.path.join(BASE_DIR, 'Listado.ods')])

ln = LectorNotasCSV('/tmp/listado.csv')

with open("/tmp/listado.csv", 'r') as archivo:
    ll = archivo.readlines()

notas = open(os.path.join(BASE_DIR, 'FormatoNotas/notas.cvs'),'w')

ltex = "%% ESTE ES EL ARCHIVO PARA LA TABLA \n"
for ind,l in enumerate(ll[:-1]):
    lsep = l.split(',')
    if ind > 0:
        obs = ln.observaciones(ind - 1)[0] 
    else:
        obs = 'Obs'

    ltex += '&'.join([c for k,c in enumerate(lsep) if k not in [3,8]]) +\
            '&' + obs + "\\\\ \n \\hline \n"

notas.write(ltex)


notas.close()
