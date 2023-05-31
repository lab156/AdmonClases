import csv
import pandas as pd
import os
from collections import Counter
import listado_utils as lu

#Define una clase que toma un archivo abierto

class LectorNotasCSV():
    def __init__(self,archivo):
        #Lee la cadena o objeto archivo 
        ## la columna Cuenta se tiene que leer como cadena
        the_rest, extension = os.path.splitext(archivo)

        match extension:
            case '.csv':
                self.df = pd.read_csv(archivo,
                               index_col=0,
                               dtype={'Cuenta':str}
                                      ).fillna(value=0.0)
            case '.ods':
                self.df = pd.read_excel(archivo, 
                            index_col=0, 
                        dtype={'Cuenta':str}).fillna(value=0.0)
                # after this the name of the index is Nº
                self.df.index.name = None
            case '.xls':
                # this is just XML
                self.df = lu.get_dataframe_from_listado(archivo)
            case other:
                raise NotImplementedError(f'The extension {extension} is not supported yet')

        #convierte el DataFrame en diccionarios de cada fila
        #ej. {'Correo Electronico': 'luisberlioz@gmail.com',
#         'Cuenta': nan,
#         'Exa 1': 48.0,
#         'Exa 2': 48.0,
#         'Nombre Completo': 'PAUTA',
#         'Nº': 12,
#         'Tarea 1': 5.0,
#         'Tarea 2': 5.0,
#         'Tarea 3': 5.0,
#         'Tarea 4': 5.0,
#         'Tarea 5': 5.0,
#         'Tarea 6': 5.0,
#         'Tarea 7': 5.0}

        self.Dlist = self.df.to_dict('records')
        self.encabezados = list(self.df.columns)


    def notas(self,examen):
        """
        Retorna una lista (sin ningun orden en especifico)
        de todas las notas validas. Para fines estadisticos

        examen: cadena con el nombre de la columna
        """
        salida = []
        for l in self.Dlist:
            try:
                if l['Nombre Completo'] != 'PAUTA': 
                    notita = float(l[examen])
                    if notita > 0:
                        salida.append(notita)
            except ValueError:
                pass
        return salida

    def list_email_addresses(self):
        salida = []

        campos = [c for c in self.encabezados if 'correo' in c.lower()]

        for l in self.Dlist:
            for camp in campos:
                salida.append(l[camp])
        return salida


    def correos_validos(self,examen,**kwargs):
        """
        Retorna una lista (sin ningun orden en especifico)
        de todos los correos con notas validas. 
        Con el proposito no enviar notificacion a los alumnos 
        que no hicieron examen.

        examen: cadena con el nombre de la columna
        """
        #SI EXAMEN ES NONE RETORNE LA LISTA COMPLETA DE TODOS LOS 
        #CORRREOS SIN NINGUNA VALIDACION

        campos = kwargs.get('campos', None)
        salida = []
        for l in self.Dlist:
            if self.es_buen_correo(l,examen):
                correos = [l.get(ef, None) for ef in campos]
                salida.append(correos)
        return salida

    def buscar_por_campo(self,direc,*args,**kwargs):
        '''
        retorna diccionario con la informacion de alumno
        dada una direccion de correo

        pn: retorna el primer nombre
        '''
        campo = kwargs.get('campo','Correo Electronico')
        for l in self.Dlist:
            if l[campo] == direc:
                if 'pn' in args:
                    return l['Nombre Completo'].split()[0]
                elif 'em' in args:
                    return l['Correo Electronico'].split()[0]
                else:
                    ##QUITA LOS ESPACIOS DE LOS KEYS PARA USAR CON CONTEXT DJANGO
                    es_para_context = kwargs.get('context',False)
                    if es_para_context:
                        return { ''.join(k.split()):l[k] for k in l }
                    else:
                        return l
        else:
            if 'pn' in args:
                return ''
            elif 'em' in args:
                return ''
            else:
                return {}

    def es_buen_correo(self,D,examen):
        '''
        D; es un diccionario de con las claves habituales
        retorna True si el diccionario pasa todas las pruebas
        por ejemplo el tiene nombre completo, numero de cuenta
        el correo pasa cierta prueba; etc.

        examen: es la cadena con el nombre de la columna del examen que hay que revisar.
        '''
        # En el caso que examen sea None, queremos la lista mas completa 
        # disponible
        if examen == None:
            return True

        nombre = D.get("Nombre Completo",False)
        if not nombre:
            return False

        #correo = D.get("Correo Electronico",False)
        #if not correo:
        #    return False

#Los alumnos de maestria no tienen numero de cuenta
        if "Cuenta" in self.encabezados:
            cuenta = D.get("Cuenta",False)
            if not cuenta:
                return False

        try:
            nota = float(D.get(examen,False))
        except ValueError:
            return False
        if not nota and nota<5:
            return False
        return True

    def pctl(self,v,examen):
        '''
        retorna el percentil de v en relacion a notas
        '''
        grades = self.notas(examen)
        grades.sort()
        i = 1
        while grades[i] < v:
            i += 1
            if i > (len(grades) - 1):
                return 100.0
        return round(abs((i - 0.5)*100/len(grades)))

    def get_col_index(self, cols):
        return [self.df.columns.get_loc(s) for s in cols]

    def nombre_nota_final(self):
        ''' 
        retorna nombre de la ultima columna de la dataframe
        normalmente esta es la columns de las notas finales
        '''
        return self.df.columns[-1]

    def observaciones(self, ind, nota_final="Total"):
        '''
        Para un indice, devuelve las observaciones en cuanto a los examenes 
        '''
        #Encontramos todas las columnas que parecen examenes
        exas = [ c for c in self.df.columns if 'exa' in c.lower() ]
        resul = self.df[exas].iloc[ind]
        final = self.df[nota_final].iloc[ind]

        #Si hizo al menos un examen se fue chuco
        if final >= 65:
            return ('APR', 'aprobado')
        else: 
            #numero de resultados positivos
            nresul = (resul>0).sum()
            if nresul == 0:
                return ('NSP', 'no se presento')
            # si hizo el primer examen
            elif nresul < len(resul) and resul[0]>0:
                return ('ABD', 'abandono')
            else:
                return ('RPB', 'reprobado')

    def latex_line(self, ind, **kwargs):
        '''
        retorna una linea en estilo latex (para la sabana)
        el argumento 'nota_final' permite controlar la columna
        que contiene las notas finales. El valor predeterminado es 
        'Total' 

        not_in: indice no deseados
        '''
        fil = list(self.df.iloc[ind].astype(str))
        obs = kwargs.get('nota_final', False)
        not_in_list = kwargs.get('not_in', [])
        if obs:
            fil.append(self.observaciones(ind, obs)[0])

        return '&'.join([f for k,f in enumerate(fil) if k not in not_in_list])

    def resultado_stats(self, col='Resul',
            cnt_dict={'APR': 0, 'RPB': 0, 'ABD': 0, 'NSP': 0},
            print_summary=True):
        '''
        retorna las estadisticas segun aprobados, reprobados, etc
        '''
        Df = self.df
        if Df[Df['Nombre Completo'].str.contains('PAUTA')].size == 0:
            print("No se encontro un renglon con PAUTA")
        else:
            print("se elimino el renglon de PAUTA")
        
        Df = Df[~Df['Nombre Completo'].str.contains('PAUTA')]
        cn = Counter(cnt_dict)
        cn.update(list(Df['Resul']))
        if print_summary:
            Total = sum(cn.values())
            print(f"| OBS | Cuenta |   %   |")
            print(f"========================")
            for obs, cant in cn.items():
                print(f"| {obs} | {cant:>6} | {100*cant/Total:>4.1f}% |")
            print(f"========================")
            print(f"Total: {Total}")
        return cn

def main():
    import argparse
    import sys
    parser = argparse.ArgumentParser(
            description='Operaciones con listados.')
    parser.add_argument('archivo', type=str)

    parser.add_argument('-e', '--estadisticas', 
        help='Imprimir las estadisticas final de una clase', 
                        action='store_true')

    parser.add_argument('-l', '--lista', 
        help='imprimir la lista de los correos de estudiantes', 
                        action='store_true')

    args = parser.parse_args(sys.argv[1:])


    listado = LectorNotasCSV(args.archivo)
    if args.estadisticas:
        listado.resultado_stats(print_summary=True)
    if args.lista:
        #for r in lu.get_dataframe_from_listado(args.archivo)\
                #        .iterrows():
            #print(f"{r[1][1]} <{r[1][2]}>")
        for r in listado.df.iterrows():
            print(f"{r[1][1]} <{r[1][2]}>")


if __name__ == "__main__":
    main()



        
        
            

