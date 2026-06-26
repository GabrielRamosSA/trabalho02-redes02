import socket
import os
import hashlib

HOST = "0.0.0.0"
PORT = 8080

PASTA_WEB = "www"

AUTH = hashlib.sha256(
    "20239042799Gabriel Ramos Santos".encode()
).hexdigest()


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


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

print("Servidor HTTP TCP iniciado...")
print(f"Escutando na porta {PORT}")

while True:
    conn, addr = server.accept()

    print(f"\nConexão recebida de {addr}")

    requisicao = conn.recv(4096).decode(errors="ignore")

    print("Requisição HTTP recebida:")
    print(requisicao)

    linhas = requisicao.splitlines()

    if len(linhas) == 0:
        conn.close()
        continue

    primeira_linha = linhas[0].split()

    if len(primeira_linha) < 2:
        conn.close()
        continue

    metodo = primeira_linha[0]
    caminho = primeira_linha[1]

    if metodo != "GET":
        corpo = b"Metodo nao permitido"
        resposta = montar_resposta("405 Method Not Allowed", "text/plain", corpo)
        conn.sendall(resposta)
        conn.close()
        continue

    if caminho == "/":
        caminho = "/index.html"

    caminho_arquivo = os.path.join(PASTA_WEB, caminho.lstrip("/"))

    if os.path.exists(caminho_arquivo) and os.path.isfile(caminho_arquivo):
        with open(caminho_arquivo, "rb") as arquivo:
            corpo = arquivo.read()

        content_type = descobrir_content_type(caminho_arquivo)

        resposta = montar_resposta("200 OK", content_type, corpo)

        print(f"Arquivo encontrado: {caminho_arquivo}")
        print("Resposta: HTTP/1.1 200 OK")

    else:
        corpo = b"<html><body><h1>404 Not Found</h1></body></html>"

        resposta = montar_resposta("404 Not Found", "text/html", corpo)

        print(f"Arquivo nao encontrado: {caminho_arquivo}")
        print("Resposta: HTTP/1.1 404 Not Found")

    conn.sendall(resposta)
    conn.close()