import socket

HOST = "0.0.0.0"
PORT = 5353

def carregar_hosts():
    tabela = {}

    with open("hosts.txt", "r") as arquivo:
        for linha in arquivo:
            partes = linha.strip().split()

            if len(partes) == 2:
                nome = partes[0]
                ip = partes[1]
                tabela[nome] = ip

    return tabela


tabela_dns = carregar_hosts()

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

print("Servidor DNS iniciado...")
print(f"Escutando na porta {PORT}")

while True:
    dados, addr = server.recvfrom(1024)

    mensagem = dados.decode()

    print(f"\nConsulta recebida de {addr}:")
    print(mensagem)

    partes = mensagem.split(";")

    id_consulta = ""
    nome = ""

    for parte in partes:
        if parte.startswith("ID="):
            id_consulta = parte.replace("ID=", "")

        if parte.startswith("NAME="):
            nome = parte.replace("NAME=", "")

    if nome in tabela_dns:
        ip = tabela_dns[nome]
    else:
        ip = "0.0.0.0"

    resposta = f"ID={id_consulta};NAME={nome};IP={ip}"

    server.sendto(resposta.encode(), addr)

    print("Resposta enviada:")
    print(resposta)