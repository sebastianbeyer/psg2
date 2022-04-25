#!/bin/bash
set -e
# set -x


if [[ $# -eq 0 ]] ; then
    echo "usage: $0 <template_grid>"
    exit 1
fi

template=$1
shapefile=$2
ncout=$3

reg_XY=$(gmt grdinfo -I- ${template})
dx=$(gmt grdinfo -Cn -o7 ${template})


# bamber="+proj=stere +lat_0=90 +lat_ts=71 +lon_0=-39 +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
# epsg3413="+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
projNHEM="+ellps=WGS84 +datum=WGS84 +lat_ts=71.0 +proj=stere +x_0=0.0 +units=m +lon_0=-44.0 +lat_0=90.0"


ogr2ogr -f "GMT" ${ncout}.temp.gmt ${shapefile} -t_srs "$projNHEM"


nPolygons=$(cat ${ncout}.temp.gmt |grep -c "@P")
echo "Found $nPolygons polygons."

polyStrings=( "other" )
polyNumbers=( 0 )

for i in $(seq 1 $nPolygons)
do
    sed -n "/D${i}/,/>/p" ${ncout}.temp.gmt |\
        awk 'NR%1==0' |\
        gmt grdmask $reg_XY \
                -I${dx} -Gpoly${i}.nc -Np${i}

    # extract polygon name:
    pName=$(sed -n "/D${i}/,/#/p" ${ncout}.temp.gmt | head -n1 | cut -d '|' -f 2)
    polyStrings+=("${pName}")
    polyNumbers+=("${i}")
    echo $i $pName
  done

# function to join array values
function join_by { local IFS="$1"; shift; echo "$*"; }
polydoc=$(join_by , "${polyStrings[@]}")
polynums=$(join_by , "${polyNumbers[@]}")


# build one file
gmt grdmath poly1.nc poly2.nc ADD poly3.nc ADD = $ncout

# remove single files
for i in $(seq 1 $nPolygons)
do
    rm -f poly${i}.nc
done

# metadata
ncrename -v z,polygon $ncout

ncatted -O -a title,global,o,c,"NHEM regions" -h $ncout
ncatted -O -a flag_meanings,polygon,c,c,"$polydoc" -h $ncout
ncatted -O -a flag_values,polygon,c,s,"$polynums" -h $ncout
ncatted -O -a projection,global,c,c,"$projNHEM" -h $ncout


# clean up
rm -f gmt.history
rm -f ${ncout}.temp.gmt

