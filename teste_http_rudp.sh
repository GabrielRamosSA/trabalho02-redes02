#!/bin/bash

CENARIO=$1

if [ -z "$CENARIO" ]; then
    echo "Uso: ./teste_http_rudp.sh A"
    exit 1
fi

rm -f resultados_http_rudp.csv

for ARQUIVO in /arquivo_100kb.bin /arquivo_1mb.bin /arquivo_5mb.bin
do
    echo "Testando R-UDP - Cenário $CENARIO - Arquivo $ARQUIVO"

    for i in {1..10}
    do
        echo "Execução $i"
        python cliente_http_rudp.py $ARQUIVO $CENARIO
        sleep 1
    done
done