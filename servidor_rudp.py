import socket
import hashlib

HOST = '0.0.0.0'
PORT = 6000

AUTH_ESPERADO = hashlib.sha256(
    "20239042799Gabriel Ramos Santos".encode()
).hexdigest()

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

print("Servidor R-UDP iniciado...")
print("Aguardando transferências...")

while True:
    print("\nEsperando X-Custom-Auth...")

    auth, addr = server.recvfrom(1024)
    auth = auth.decode()

    print("X-Custom-Auth recebido:")
    print(auth)

    if auth != AUTH_ESPERADO:
        print("Auth inválido!")
        continue

    print("Auth válido!")

    nome_arquivo = "recebido_rudp.exe"

    with open(nome_arquivo, "wb") as arquivo:
        while True:
            pacote, addr = server.recvfrom(9000)

            if pacote == b'FIM':
                break

            seq = pacote[:10].decode().strip()
            checksum_recebido = pacote[10:42].decode()
            dados = pacote[42:]

            checksum_calculado = hashlib.md5(dados).hexdigest()

            if checksum_recebido == checksum_calculado:
                print(f"Pacote {seq} OK")

                arquivo.write(dados)

                ack = f"ACK{seq}".encode()
                server.sendto(ack, addr)

            else:
                print(f"Pacote {seq} corrompido")

    print("Arquivo recebido com sucesso.")
    print("Pronto para próxima transferência.")