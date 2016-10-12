#!/bin/bash

graphs=`find . -name "*.dot"`
tot=0
for f in ${graphs}; do 
    tot=$((tot+1))
done

i=0;
for f in ${graphs}; do 
    i=$((i+1))
    echo "Processing ${i}/${tot}"

    dst="${f%.*}.svg";
    tmp_file="${f}tmp"

    `cat $f | grep -v "dotted" > ${tmp_file}`;   
    dot -Tsvg -o${dst} "${tmp_file}";
    rm "${tmp_file}";
done
