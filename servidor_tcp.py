import socket
import time
import hashlib

HOST = '0.0.0.0'
PORT = 5000

AUTH_ESPERADO = hashlib.sha256(
    "20239042799Gabriel Ramos Santos".encode()
).hexdigest()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

print("Servidor TCP iniciado...")
print("Aguardando conexões...")

while True:

    conn, addr = server.accept()

    print(f"\nConectado com {addr}")

    auth = conn.recv(64).decode()

    print("X-Custom-Auth recebido:")
    print(auth)

    if auth != AUTH_ESPERADO:
        print("Auth inválido!")
        conn.close()
        continue

    print("Auth válido!")

    inicio = time.time()

    with open("recebido_tcp.txt", "wb") as f:

        while True:

            dados = conn.recv(1024)

            if not dados:
                break

            f.write(dados)

    fim = time.time()

    tempo = fim - inicio

    print(f"Arquivo recebido em {tempo:.6f} segundos")

    conn.close()

    print("Conexão encerrada.")
    print("Aguardando próxima conexão...")