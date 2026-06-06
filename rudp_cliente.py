import socket
import hashlib
import time
import os

SERVER_IP = 'servidor'
PORT = 6000

NOME_ARQUIVO = "arquivo_teste.bin"

AUTH = hashlib.sha256(
    "20239042799Gabriel Ramos Santos".encode()
).hexdigest()

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(1)

client.sendto(AUTH.encode(), (SERVER_IP, PORT))

seq = 0
retransmissoes = 0

inicio = time.time()

with open(NOME_ARQUIVO, "rb") as f:
    while True:
        dados = f.read(8192)

        if not dados:
            break

        checksum = hashlib.md5(dados).hexdigest()
        cabecalho = f"{seq:<10}".encode()

        pacote = cabecalho + checksum.encode() + dados

        while True:
            client.sendto(pacote, (SERVER_IP, PORT))

            try:
                ack, _ = client.recvfrom(1024)

                if ack.decode() == f"ACK{seq}":
                    break

            except socket.timeout:
                retransmissoes += 1
                print(f"Timeout pacote {seq}, retransmitindo")

        seq += 1

client.sendto(b'FIM', (SERVER_IP, PORT))

fim = time.time()

tamanho = os.path.getsize(NOME_ARQUIVO)

tempo = fim - inicio
throughput = tamanho / tempo / 1024

with open("resultados_rudp.csv", "a") as arq:
    arq.write(f"{tempo},{throughput},{retransmissoes}\n")

print(f"Tempo: {tempo:.6f} segundos")
print(f"Throughput: {throughput:.2f} KB/s")
print(f"Retransmissões: {retransmissoes}")

client.close()