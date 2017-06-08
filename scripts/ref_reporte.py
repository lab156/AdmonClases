import os
import sys

notas_file = os.path.join(os.curdir, sys.argv[1])
repor_file = os.path.join(os.curdir, sys.argv[2])

with open(notas_file, 'r') as notas_f:
    notas = notas_f.readlines()


obser = [s.split("&")[-1][:3] for s in notas if s.split("&")[-1][:3] in ['APR', 'RPB', 'ABD', 'NSP']]


nsp = sum([1 for o in obser if o == 'NSP'])
abd = sum([1 for o in obser if o == 'ABD'])
apr = sum([1 for o in obser if o == 'APR'])
rpb = sum([1 for o in obser if o == 'RPB'])
tot_desert = nsp + abd
tot_eval = rpb + apr

repor_str = "   REPORTE ESTADISTICO \n"
repor_str += "Desertores" +\
        "Total Desertores: " + repr(tot_desert)  + '\n' +\
        "NSP: " + repr(nsp) + '\n' +\
        "ABD: " + repr(abd) + '\n' +\
        "Evaluados" + '\n' +\
        "Total Evaluados: " + repr(tot_eval) + '\n' +\
        "APR: " + repr(apr) +'\n'  +\
        "RPB: " + repr(rpb) + '\n' 

with open(repor_file, 'w') as repor_f:
    repor = repor_f.write(repor_str)
