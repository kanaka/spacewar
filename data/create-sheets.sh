#!/bin/bash

obj_sheet_file=
obj() {
    local name=$1 x=$2 y=$3 w=$4 h=$5 last=$6
    echo -n "  {\"frame\": {\"x\": $x, \"y\": $y, \"w\": $w, \"h\": $h}," >> ${obj_sheet_file}
    echo -n " \"filename\": \"$name\"}" >> ${obj_sheet_file}
    [ -z "$last" ] && echo "," >> ${obj_sheet_file} || echo >> ${obj_sheet_file}
}


for s in $(seq 0 3); do
    convert '(' ship$((1+${s}))-up{,-boost2,-boost1}.png +append ')' \
            ship-teleport.png \
            ship-warp.png \
            -append \
            -background transparent \
            sheet-ship${s}.png

    obj_sheet_file=sheet-ship${s}.json
    y=0

    echo "{\"frames\": [" > ${obj_sheet_file}

    obj main 0 ${y} 32 32
    for a in $(seq 0 3); do
        obj thrust${a} $(( 32+a*32 )) ${y} 32 32
    done
    for a in $(seq 0 3); do
        obj reverse${a} $(( 160+a*32 )) ${y} 32 32
    done
    y=$(( y+32 )) 

    # Teleport
    for i in $(seq 0 23); do
        obj teleport${i} $(( i*32 )) ${y} 32 32
    done
    y=$(( y+32 ))

    # Warp
    for i in $(seq 0 11); do
        obj warp${i} $(( i*48 )) ${y} 48 32
    done
    y=$(( y+32 ))

    # Ending item
    obj nothing 0 0 1 1 true

    echo "]}" >> ${obj_sheet_file}
done
