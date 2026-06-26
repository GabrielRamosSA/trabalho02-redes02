#!/bin/bash

CENARIO=$1

if [ -z "$CENARIO" ]; then
    echo "Uso: ./teste_http_tcp.sh A"
    exit 1
fi

rm -f resultados_http_tcp.csv

for ARQUIVO in /arquivo_100kb.bin /arquivo_1mb.bin /arquivo_5mb.bin
do
    echo "Testando TCP - Cenário $CENARIO - Arquivo $ARQUIVO"

    for i in {1..10}
    do
        echo "Execução $i"
        python cliente_http_tcp.py $ARQUIVO $CENARIO 
        sleep 1
    done
done