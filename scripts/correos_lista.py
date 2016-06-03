import lector_notas as Lector
import subprocess
import sys


subprocess.call(["unoconv", "-f", "csv", "-e", "FilterOptions=44,34,76", "-o", "/tmp/listado.csv", "%s"%sys.argv[1]])


with open("/tmp/listado.csv", 'r') as archivo:
    L = Lector.LectorNotasCSV(archivo)


for l in L.list_email_addresses():
    if type(l) == str:
        print(l+';')
