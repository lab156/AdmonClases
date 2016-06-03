#!/bin/bash

#   Usage:
#   Default value
#     $ create_new_clase.sh [number of the class you want to create]
#   -t <number>
#   el numero de la tarea que se esta creando
#   -h <dirname>
#   the flag -h nameofdir to create directory for homeworks
#   -e <dirname>
#   create a exam directory
#   Example:
#   To create the file of class 4 quickly:
#    $ ./create_new_clase.sh 4
#   
# run with no arguments to create the next lecture file

#GET THE NAME OF THE CURRENT DIRECTORY
CURRDIR=${PWD##*/}

if [ "$CURRDIR" == AdmonClases ];
then
    echo "Currently working in local dir: "$CURRDIR
    GETDIR="./"
else
    GETDIR="./AdmonClases/"
fi


# CHECK IF THE COURSE CONFIGURATION FILE IS AVAILABLE
if [ -e course_info ]; 
then
   source course_info 
else
   echo "No hay archivo de configuracion; copielo de la carpeta templates y completelo"
   exit 10
fi

#SET LANGUAGE
case $COURSELANG in
    en)
        STYLEFILE=$GETDIR"styles/general.sty"
        ;;
    es)
        echo "setting lang to spanish"
        STYLEFILE=$GETDIR"styles/general_es.sty"
        ;;
    \?)
        echo "lenguaje $COURSELANG no reconocido"
        exit 2
        ;;
esac

#DEFAULT OPTIONS
FILESUFFIX=class
#PREFIX TO LOOKUP IN TEMPLATES
FILEPREFIX=this
NAMEOFDIR=$1

while getopts t:h:e:sfl opt; do
    case $opt in
        h)
            echo "Creating new hw dir: $OPTARG" >&2
            FILESUFFIX=paper
            NAMEOFDIR=$OPTARG
            ;;
        t)
            echo "Creando directorio: tarea$OPTARG" >&2
            FILESUFFIX=tarea
            TAREANUM=$OPTARG
            NAMEOFDIR=tarea$OPTARG
            ;;
        e)
            echo "Creating new exam dir: $OPTARG" >&2
            read -p "Que Parcial? (ej. primer) " ORDINAL_LOW
            ORDINAL=${ORDINAL_LOW^^}
            FILESUFFIX=exam
            NAMEOFDIR=$OPTARG
            ;;
        f) echo "Creating new FormatoNotas dir" >&2
            NAMEOFDIR=FormatoNotas
            ;;
        s)
            echo "Creando el Silabo de la clase"
            FILESUFFIX=silabo
            NAMEOFDIR=silabo
            ;;

        l) 
            echo "Lista de correos de $COURSENAME" >&2
            python ${GETDIR}scripts/correos_lista.py ${PWD}/Listado.ods
            exit 0
            ;;
        \?)
            echo "Invalid Option" >&2
            exit 2
            ;;
    esac
done


#RETURNS THE NAME OF THE FILE WITH THE LARGEST NUMERIC VALUE
function last_lecture {
regu="^[0-9]+$"
for fil in `ls`; do 
    if [[ $fil =~ $regu ]]; then 
        echo $fil;
    fi; 
done | sort -n | tail -1
}

#FUNCTION THAT CREATES A DIRECTORY AND ITS LINKS 
function new_dir {
    mkdir $1 &&\
        plantillar2 ${GETDIR}templates/${FILEPREFIX}_$FILESUFFIX.tex $ORDINAL>$1/${COURSECODE}_$NAMEOFDIR.tex  &&\
        touch $1/$FILESUFFIX.tex &&\
        #It appears that ln only works when they are created from 
        #the inside of the directory
        cd $1 &&\
        ln -s ../$STYLEFILE ./general.sty 
        cd ..
    }

function plantillar2 {
template_file=$1

sed -e "s;%COURSENAME%;$COURSENAME;g"\
    -e "s;%ORDINAL%;$2;g"\
    -e "s;%COURSECODE%;$COURSECODE;g"\
    -e "s;%TAREANUM%;$TAREANUM;g" $1
}

        #add the line to the TEX file
function add_to_tex_file {
        TEXNOTES=${COURSETARGETNAME}_notes.tex
        if [ ! -e $TEXNOTES ]; 
        then
        echo "NO hay archivo de $TEXNOTES notas... lo jalamos de templates" 
        cp ${GETDIR}templates/notes_default.tex $TEXNOTES
        fi
        match='\\end{document}'
        insert='\\input{'$1'/'$FILESUFFIX'}'
        sed -i "s@$match@$insert\n$match@" $TEXNOTES
    }

if [ "$NAMEOFDIR" == "" ] ; then
    ll=`last_lecture`
    if [[ $ll == "" ]]; then
        #NO RESULTS; CREATE FIRST DIR
        new_name=1;
    else
        new_name=$(( 1 + $ll ));
    fi
    echo Creating new dir $new_name
   new_dir $new_name 
   add_to_tex_file $new_name
    exit 0
elif [ -a $NAMEOFDIR ] ; then
    echo "The file already exists!!!"
    exit 1
elif [ "$NAMEOFDIR" == "FormatoNotas" ] ; then
    mkdir $NAMEOFDIR
    ${GETDIR}scripts/plantillar.sh ${GETDIR}templates/formato.tex $ORDINAL>\
        $NAMEOFDIR/formato.tex &&\
        ${GETDIR}scripts/formateador.py &&\
        cp ${GETDIR}images/logo.jpg $NAMEOFDIR
    exit 0
else
    new_dir $NAMEOFDIR
    exit 0
fi
