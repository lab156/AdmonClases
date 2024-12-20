import matplotlib.pyplot as plt
import os
import sys
import smtplib as s
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
#import msg_functions as ms
from lector_notas import LectorNotasCSV
#from django.template import Template, Context
#from django.conf import settings
from jinja2 import Template, exceptions
import subprocess
import argparse
import time
import listado_utils as lu
from dotenv import load_dotenv
#from config_correo import Config
#C = Config()
#settings.configure()

_ = load_dotenv()

#Parser for the commandline options
argus = argparse.ArgumentParser(description="Enviar correo a los alumnos")
#argus.add_argument('listado', help="Ubicacion del archivo con los listados")

argus.add_argument('mens', type=str, help="Ubicacion del archivo con la plantilla del mensaje")

argus.add_argument('-l', '--listado', default="Listado.ods", type=str, help="Nombre del archivo con las notas y correos y nombres.")

argus.add_argument('--hoysi', dest='to_all', action='store_true', default=False, help="Enviar correo a todos los destinatario, sin esta opcion el correo solo se manda a Luis.")

argus.add_argument('--hist', dest='hist', action='store_true', default=False, help="Generar y adjuntar un histograma de frecuencias de notas.")

argus.add_argument('-a', '--attach', type=str,  help="Adjuntar un archivo al mensaje, por ejemplo el pdf de una tarea.")

argus.add_argument('-n', '--exanum', type=str,  help="Especificar el encabezado de la columna a examinar ej. Exa 1")
    
argus.add_argument('-c', '--correos', type=str, nargs='*',
        help="Las columnas denominadas correos para sacar la lista de destinatarios")

argus.add_argument('-s', '--subject', type=str,  help="El asunto del correo a enviar.")

args = argus.parse_args()

#CONVERTIMOS EL ARCHIVO A CSV
#unoconv_proc = subprocess.Popen(["unoconv", "-f", "csv", "-e", "FilterOptions=44,34,76", "-o", "/tmp/listado.csv", "%s"%"Listado.ods"])
#unoconv_proc.wait()

#aca pongo el examen que quiero
#es necesario porque de ahi saco los correos validos
if args.exanum == None:
    examen_num = None
else:
    examen_num = args.exanum

#with open("/tmp/listado.csv", 'r') as archivo:
archivo = args.listado 
L = LectorNotasCSV(archivo)
#
# DATA IN THIS ORDER NAME, GRADE, EMAIL --- 
if examen_num is not None:
    grades = L.notas(examen_num)
# IN ORDER TO GET THE PERCENTILES WE NEED TO SORT THE GRADES
    grades.sort()


#La lista de los destinatarios (posiblemente diferente debido a los correos mal
#ingreados al sistema)
if args.to_all:
    if args.correos == None:
        raise ValueError('No hay Correos y --hoysi es True')
    else:
        ListaDestinatarios = L.correos_validos(examen_num, campos=args.correos)
else:
    ListaDestinatarios = []
ListaDestinatarios.append(['luisberlioz@gmail.com' ])



def connect(email_address, email_port):
    try:
        serv = s.SMTP(email_address, email_port)
        #serv = s.SMTP('smtp.gmail.com', 587)
        print('ehlo 1...')
        serv.ehlo()
        print('ehlo 1 rec...')
        serv.starttls()
        print('ehlo 2...')
        serv.ehlo()
        print('ehlo 2 rec...')
        print('logging in...')
        try:
            email_passw = os.environ['UNAHEMAILPASSW']
        except KeyError:
            raise KeyError('Falta la contrasena del correo')
        serv.login('luis.berlioz@unah.edu.hn', email_passw, initial_response_ok=True)
        print('logged in...')
    except socket.gaierror:
        raise RuntimeError('El correo de la U si puede ser mierda; no esta aceptando.')
    return serv

serv = connect('outlook.office365.com', 587)

#THE TEMPLATE SHOULD ONLY BE CREATED ONCE FOR EFFICIENCY
#WHAT CHANGES IS THE CONTEXT
with open(args.mens ,'r') as archivo:
    tem = Template(archivo.read())

def histograma(grades, examen_num,  guardar_en='/tmp/Histogram.png'):
    plt.figure(figsize=(10, 6))
    plt.hist(grades, bins=7, facecolor=(0.9, 0.9, 0.9))
    mens_x = 26
    mens_y = 1.7
    plt.arrow(mens_x,mens_y,(-mens_x+nota)*0.95,-mens_y*0.8, head_width=0.01*mens_x, head_length=0.15*mens_y,color='red')
    plt.title('Percentil de tu nota: %s%% %s'%(L.pctl(nota,examen_num),examen_num))
    plt.text(mens_x*0.95,mens_y*(1.04) ,'Tu Nota: %s'%nota, color='red')
    plt.ylabel('Frecuencia de las notas')
    plt.xlabel('Notas Posibles')
    plt.savefig(guardar_en)
    plt.close()

#    msg = MIMEMultipart()
#    msg['From'] = 'Luis Berlioz <luis.berlioz@unah.edu.hn>'
#    msg['To'] = li
#    msg['Date'] = formatdate(localtime = True)
#    msg['Subject'] = 'Tu nota final'

for sublista in ListaDestinatarios:
    for li,cpo in zip(sublista, args.correos):
        if li:
            Diccion = L.buscar_por_campo(li,context=True, campo=cpo) 
            Diccion['pri_nombre'] = L.buscar_por_campo(li,'pn', campo=cpo).capitalize()
            nota = float(L.buscar_por_campo(li, campo=cpo).get(examen_num,-1))
            #contex = Context(Diccion)
            contex = Diccion


            msg = MIMEMultipart()
            msg['From'] = 'Luis Berlioz <luis.berlioz@unah.edu.hn>'
            msg['To'] = li
            msg['Date'] = formatdate(localtime = True)
            msg['Subject'] = args.subject


            try:
                MensajeCorreo = tem.render(contex)
            except exceptions.UndefinedError as K:
                print('Al parecer %s no tiene %s'%(Diccion['pri_nombre'], cpo))
                print('Ocurrio un KeyError: %s estas seguro que PAUTA esta bien escrito con mi correo en el campo de correo personal?'%K)
                sys.exit(1)

            with open('message_preview.html', 'w') as preview:
                preview.write(MensajeCorreo)

            msg.attach( MIMEText(MensajeCorreo, 'html')) 

            if args.attach is not None:
                tareaf = os.path.join(os.curdir,args.attach)
                file_lst = os.listdir(tareaf)
                for f in file_lst:
                    if f.startswith('MM') and f.endswith('.pdf'):
                        fname = os.path.join(tareaf,f)
                        
                part = MIMEBase('application', 'octet-stream')
                part.set_payload( open(fname,'rb').read() )
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; \
                        filename="{0}"'.format(os.path.basename(fname)))
                    
                msg.attach(part)



# ACA ADJUNTAMOS LA IMAGEN GENERADA CON MATPLOTLIB
            if args.hist:
                histograma(grades, examen_num)
                part = MIMEBase('application', 'octet-stream')
                part.set_payload( open('/tmp/Histogram.png','rb').read() )
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; \
                        filename="{0}"'.format(os.path.basename('/tmp/Histogram.png')))
                msg.attach(part)



            try: 
                serv.sendmail('luis.berlioz@unah.edu.hn', li , msg.as_string())
                print('Email successfully sent to %s email: %s'%(Diccion['pri_nombre'],li))
            except AttributeError:
                print('Fallo envio a %s con correo %s'%(Diccion['pri_nombre'],li))
            except s.SMTPSenderRefused:
                print('Vergueo del sender rate!! Esperando 30 segundos')
                time.sleep(30)
                serv = connect('outlook.office365.com', 587)
                #Volvemos a intentar mandas el mensaje
                serv.sendmail('luis.berlioz@unah.edu.hn', li , msg.as_string())
                print('Email successfully sent to %s email: %s'%(Diccion['pri_nombre'],li))

serv.close()

