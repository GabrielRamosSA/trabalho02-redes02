import socket
import time
import os
import hashlib

SERVER_IP = 'servidor'
PORT = 5000

NOME_ARQUIVO = "arquivo_teste.bin"

AUTH = hashlib.sha256(
    "20239042799Gabriel Ramos Santos".encode()
).hexdigest()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((SERVER_IP, PORT))

client.send(AUTH.encode())

time.sleep(0.1)

inicio = time.time()

with open(NOME_ARQUIVO, "rb") as f:
    while True:
        dados = f.read(1024)

        if not dados:
            break

        client.send(dados)

fim = time.time()

tamanho = os.path.getsize(NOME_ARQUIVO)

tempo = fim - inicio
throughput = tamanho / tempo / 1024

with open("resultados_tcp.csv", "a") as arq:
    arq.write(f"{tempo},{throughput}\n")

print(f"Tempo: {tempo:.6f} segundos")
print(f"Throughput: {throughput:.2f} KB/s")

client.close()