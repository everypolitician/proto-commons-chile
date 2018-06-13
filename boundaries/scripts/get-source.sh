#!/bin/bash
# To call the script open the terminal in the same folder as the script
# Ensure it is executable: $ chmod u+x merge-reproject.sh
# Call it with the layer you wish to combine: eg. $ ./get-source.ch Comuna
# LAYERS are 'Comuna' 'Region' and 'Provincia'


LYR=$1


#SET TO PATH WHERE YOU WANT THE SHP TO BE CREATED
FILE="../source/${LYR}-5361.shp" # name of file to be merged to
LAYER="${LYR}-5361" # should be the same as
TSRS='EPSG:5361' # target CRS
BASE='/vsizip//vsicurl/http://www.ine.cl/docs/default-source/herramientas/galeria-de-mapas/cartograf%c3%ada-precenso-2016'


for i in {01..15}

do
    SRC="$BASE/r$i.zip/R$i/${LYR}.shp"


    if [ -f "$FILE" ]
        then
                echo "Reprojecting and merging $SRC..."
                ogr2ogr \
                -f 'ESRI Shapefile' \
                -t_srs $TSRS \
                -update -append $FILE $SRC \
                -nln $LAYER
        else
                echo "creating $FILE..."
                ogr2ogr \
                -f 'ESRI Shapefile' \
                -t_srs $TSRS \
                $FILE $SRC

    fi
done
