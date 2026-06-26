import socket
import hashlib
import os

HOST = "0.0.0.0"
PORT = 8081

PASTA_WEB = "www"
TAMANHO_BLOCO = 8192

AUTH = hashlib.sha256(
    "20239042799Gabriel Ramos Santos".encode()
).hexdigest()


def calcular_checksum(dados):
    return hashlib.md5(dados).hexdigest()


def montar_pacote(seq, dados):
    checksum = calcular_checksum(dados)
    cabecalho = f"{seq:<10}".encode() + checksum.encode()
    return cabecalho + dados


def enviar_confiavel(sock, addr, dados):
    seq = 0
    retransmissoes = 0

    for i in range(0, len(dados), TAMANHO_BLOCO):
        bloco = dados[i:i + TAMANHO_BLOCO]
        pacote = montar_pacote(seq, bloco)

        while True:
            sock.sendto(pacote, addr)

            try:
                ack, _ = sock.recvfrom(1024)
                ack = ack.decode()

                if ack == f"ACK{seq}":
                    break

            except socket.timeout:
                retransmissoes += 1
                print(f"Timeout ao enviar pacote {seq}, retransmitindo")

        seq += 1

    sock.sendto(b"FIM", addr)

    return retransmissoes


def receber_confiavel(sock):
    dados_completos = b""
    addr_cliente = None

    while True:
        pacote, addr = sock.recvfrom(9000)
        addr_cliente = addr

        if pacote == b"FIM":
            break

        seq = pacote[:10].decode().strip()
        checksum_recebido = pacote[10:42].decode()
        dados = pacote[42:]

        checksum_calculado = calcular_checksum(dados)

        if checksum_recebido == checksum_calculado:
            dados_completos += dados
            ack = f"ACK{seq}".encode()
            sock.sendto(ack, addr)

        else:
            print(f"Pacote {seq} corrompido")

    return dados_completos, addr_cliente


def descobrir_content_type(caminho):
    if caminho.endswith(".html"):
        return "text/html"
    elif caminho.endswith(".css"):
        return "text/css"
    elif caminho.endswith(".js"):
        return "application/javascript"
    elif caminho.endswith(".png"):
        return "image/png"
    elif caminho.endswith(".jpg") or caminho.endswith(".jpeg"):
        return "image/jpeg"
    else:
        return "application/octet-stream"


def montar_resposta(status, content_type, corpo):
    cabecalho = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(corpo)}\r\n"
        f"X-Custom-Auth: {AUTH}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )

    return cabecalho.encode() + corpo


def processar_requisicao(requisicao):
    print("\nRequisição HTTP recebida via R-UDP:")
    print(requisicao)

    linhas = requisicao.splitlines()

    if len(linhas) == 0:
        corpo = b"Requisicao invalida"
        return montar_resposta("400 Bad Request", "text/plain", corpo)

    partes = linhas[0].split()

    if len(partes) < 2:
        corpo = b"Requisicao invalida"
        return montar_resposta("400 Bad Request", "text/plain", corpo)

    metodo = partes[0]
    caminho = partes[1]

    if metodo != "GET":
        corpo = b"Metodo nao permitido"
        return montar_resposta("405 Method Not Allowed", "text/plain", corpo)

    if caminho == "/":
        caminho = "/index.html"

    caminho_arquivo = os.path.join(PASTA_WEB, caminho.lstrip("/"))

    if os.path.exists(caminho_arquivo) and os.path.isfile(caminho_arquivo):
        with open(caminho_arquivo, "rb") as arquivo:
            corpo = arquivo.read()

        content_type = descobrir_content_type(caminho_arquivo)

        print(f"Arquivo encontrado: {caminho_arquivo}")
        print("Resposta: HTTP/1.1 200 OK")

        return montar_resposta("200 OK", content_type, corpo)

    else:
        corpo = b"<html><body><h1>404 Not Found</h1></body></html>"

        print(f"Arquivo nao encontrado: {caminho_arquivo}")
        print("Resposta: HTTP/1.1 404 Not Found")

        return montar_resposta("404 Not Found", "text/html", corpo)


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))
server.settimeout(1)

print("Servidor HTTP R-UDP iniciado...")
print(f"Escutando na porta {PORT}")

while True:
    try:
        dados_requisicao, addr = receber_confiavel(server)

        if not dados_requisicao:
            continue

        requisicao = dados_requisicao.decode(errors="ignore")

        resposta = processar_requisicao(requisicao)

        print("Enviando resposta HTTP via R-UDP...")

        retransmissoes = enviar_confiavel(server, addr, resposta)

        print("Resposta enviada com sucesso.")
        print(f"Retransmissões no envio da resposta: {retransmissoes}")

    except socket.timeout:
        continue