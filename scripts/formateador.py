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
notas_finales_col = ln.nombre_nota_final()

Lista = ['Nº', 'Cuenta', 'Nombre Completo', 'Exa1', 'Exa2', 'Exa3', 'Final']
col_lst = ln.get_col_index(Lista)

with open("/tmp/listado.csv", 'r') as archivo:
    ll = archivo.readlines()

def check_float(s):
    if re.match('^[0-9]+\.+[0-9]+$', s):
        return '{0:3.2f}'.format(float(s))
    else:
        return s


notas = open(os.path.join(BASE_DIR, 'FormatoNotas/notas.cvs'),'w')
repor = open(os.path.join(BASE_DIR, 'FormatoNotas/reporte.cvs'),'w')

ltex = "%% ESTE ES EL ARCHIVO PARA LA TABLA \n"
repor_str = "   REPORTE ESTADISTICO \n"
tot_desert = 0
tot_eval = 0
nsp = 0
abd = 0
apr = 0
rpb = 0
for ind,l in enumerate(ll[:-1]):
    lsep = l.split(',')
    if ind > 0:
        obs = ln.observaciones(ind - 1, nota_final=notas_finales_col)[0] 
        if obs == 'APR':
            apr += 1
            tot_eval += 1
        elif obs == 'RPB':
            rpb += 1
            tot_eval += 1
        elif obs == 'ABD':
            abd += 1
            tot_desert += 1
        elif obs == 'NSP':
            nsp += 1
            tot_desert += 1
    else:
        obs = 'Obs'

    ltex += '&'.join([check_float(c) for k,c in enumerate(lsep) if k in col_lst ]) +\
            '&' + obs + "\\\\ \n \\hline \n"

repor_str += "Desertores" +\
        "Total Desertores: " + repr(tot_desert)  + '\n' +\
        "NSP: " + repr(nsp) + '\n' +\
        "ABD: " + repr(abd) + '\n' +\
        "Evaluados" + '\n' +\
        "Total Evaluados: " + repr(tot_eval) + '\n' +\
        "APR: " + repr(apr) +'\n'  +\
        "RPB: " + repr(rpb) + '\n' 



notas.write(ltex)
repor.write(repor_str)


notas.close()
repor.close()
