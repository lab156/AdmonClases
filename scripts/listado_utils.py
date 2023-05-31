from lxml import etree
import pandas as pd
import sys

def get_dataframe_from_listado(path):
    '''
    Crea una pandas dataframe de un listado (.xls) de la Unah
    '''
    li = etree.parse(path)
    tr_lst = li.findall('//tr')
    row_it = li.getiterator('tr')
    headers = [h.text for h in next(row_it).findall('./th')]
    # first tr field contains headers has format:
    #'<tr style="color:White;background-color:#006699;font-weight:bold;">
      #<th scope="col">N&#186;</th>
      #<th scope="col">Cuenta</th>
      #<th scope="col">Nombre Completo</th>
      #<th scope="col">Correo Institucional</th>
    #</tr>'
    indices = []
    nombres = []
    cuentas = []
    correos = []
    #print(etree.tostring(headers))
    for l, row in enumerate(row_it):
        col_lst = row.findall('./td')
        for k, L in enumerate([indices, cuentas, nombres,correos]):    
            if k == 0:
                # revisamos que el indice 
                line_index = int(col_lst[k].text)
                assert l == line_index - 1
                L.append(line_index)
            else:
                data_entry = col_lst[k].text
                L.append(data_entry)
    
    alumnos_df = pd.DataFrame({
        headers[1]: cuentas,
        headers[2]: nombres,
        headers[3]: correos,
            },
    index=indices)
    
    return alumnos_df

def read_ods_listado(path):
    '''
    returns a pandas dataframe out of Listado.ods located at path 
    '''
    listado = pd.read_excel(path)
    listado = listado.fillna(0) 
    return listado


def main():
    for r in get_dataframe_from_listado(listado_path).iterrows():
        print(f"{r[1][1]} <{r[1][2]}>")

if __name__ == "__main__":
    listado_path = sys.argv[1]
    main()



