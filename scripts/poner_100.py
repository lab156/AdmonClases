# Install helium first
import helium as he


def poner_100():
    # Esta funcion le pone 100 de nota
    # y guarda al final
    he.write('100', into='Calif')
    he.click(he.TextField("Obser"))
    he.click("APR")
    he.click("Guardar")
