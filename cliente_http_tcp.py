import socket
import random
import time
import hashlib
import sys

DNS_SERVER = "172.30.0.53"
DNS_PORT = 5353

DOMINIO = "www.meusite.local"
HTTP_PORT = 8080

AUTH = hashlib.sha256(
    "20239042799Gabriel Ramos Santos".encode()
).hexdigest()


def resolver_dns(nome):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(2)

    id_consulta = random.randint(1000, 9999)
    mensagem = f"ID={id_consulta};NAME={nome}"

    inicio = time.time()

    try:
        client.sendto(mensagem.encode(), (DNS_SERVER, DNS_PORT))
        resposta, _ = client.recvfrom(1024)

        fim = time.time()
        resposta = resposta.decode()

        ip = None

        for parte in resposta.split(";"):
            if parte.startswith("IP="):
                ip = parte.replace("IP=", "")

        tempo_dns = fim - inicio

        print("Consulta DNS enviada:")
        print(mensagem)

        print("\nResposta DNS recebida:")
        print(resposta)

        print(f"\nIP resolvido: {ip}")
        print(f"Tempo DNS: {tempo_dns:.6f} segundos")

        client.close()
        return ip, tempo_dns

    except socket.timeout:
        fim = time.time()
        print("Timeout na consulta DNS.")
        client.close()
        return None, fim - inicio


def requisicao_http_tcp(ip_servidor, caminho):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    inicio = time.time()

    client.connect((ip_servidor, HTTP_PORT))

    requisicao = (
        f"GET {caminho} HTTP/1.1\r\n"
        f"Host: {DOMINIO}\r\n"
        f"X-Custom-Auth: {AUTH}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )

    client.sendall(requisicao.encode())

    resposta = b""

    while True:
        dados = client.recv(4096)

        if not dados:
            break

        resposta += dados

    fim = time.time()
    client.close()

    tempo_http = fim - inicio
    tamanho = len(resposta)
    throughput = tamanho / tempo_http / 1024

    print("\nResposta HTTP recebida:")
    print(resposta[:300].decode(errors="ignore"))

    print(f"\nTempo HTTP TCP: {tempo_http:.6f} segundos")
    print(f"Tamanho da resposta: {tamanho} bytes")
    print(f"Throughput: {throughput:.2f} KB/s")

    return tempo_http, tamanho, throughput


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python cliente_http_tcp.py /arquivo_100kb.bin A")
        exit()

    caminho = sys.argv[1]
    cenario = sys.argv[2]

    inicio_total = time.time()

    ip, tempo_dns = resolver_dns(DOMINIO)

    if ip is None or ip == "0.0.0.0":
        print("Nao foi possivel resolver o dominio.")
        exit()

    tempo_http, tamanho, throughput = requisicao_http_tcp(ip, caminho)

    fim_total = time.time()
    tempo_total = fim_total - inicio_total

    with open("resultados_http_tcp.csv", "a") as arquivo:
        arquivo.write(
            f"{cenario},{caminho},{tempo_dns},{tempo_http},{tempo_total},{tamanho},{throughput}\n"
        )

    print(f"\nTempo total DNS + HTTP TCP: {tempo_total:.6f} segundos")