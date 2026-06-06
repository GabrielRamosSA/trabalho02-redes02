#!/bin/bash

rm -f resultados_tcp.csv

for i in {1..10}
do
    echo "Execução $i"
    python cliente_tcp.py
    sleep 1
done