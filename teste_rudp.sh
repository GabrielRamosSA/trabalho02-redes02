#!/bin/bash

rm -f resultados_rudp.csv

for i in {1..10}
do
    echo "Execução $i"
    python rudp_cliente.py
    sleep 1
done