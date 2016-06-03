#! /usr/bin/python3
import subprocess
import sys
import os
import re
from lector_notas import LectorNotasCSV

#Get the path to the main dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

subprocess.call(["unoconv", "-f", "csv", "-e", "FilterOptions=44,34,76", "-o", "/tmp/listado.csv", "%s"%os.path.join(BASE_DIR, 'Listado.ods')])

ln = LectorNotasCSV('/tmp/listado.csv')

with open("/tmp/listado.csv", 'r') as archivo:
    ll = archivo.readlines()

def check_float(s):
    if re.match('^[0-9]+\.+[0-9]+$', s):
        return '{0:3.2f}'.format(float(s))
    else:
        return s


notas = open(os.path.join(BASE_DIR, 'FormatoNotas/notas.cvs'),'w')

ltex = "%% ESTE ES EL ARCHIVO PARA LA TABLA \n"
for ind,l in enumerate(ll[:-1]):
    lsep = l.split(',')
    if ind > 0:
        obs = ln.observaciones(ind - 1)[0] 
    else:
        obs = 'Obs'

    ltex += '&'.join([check_float(c) for k,c in enumerate(lsep) if k not in list(range(3,14))+[17]]) +\
            '&' + obs + "\\\\ \n \\hline \n"

notas.write(ltex)


notas.close()
