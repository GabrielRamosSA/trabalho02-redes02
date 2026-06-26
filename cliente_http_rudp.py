import socket
import random
import time
import hashlib
import sys

DNS_SERVER = "172.30.0.53"
DNS_PORT = 5353

DOMINIO = "www.meusite.local"
HTTP_RUDP_PORT = 8081

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
                print(f"Timeout pacote {seq}, retransmitindo")

        seq += 1

    sock.sendto(b"FIM", addr)

    return retransmissoes


def receber_confiavel(sock):
    dados_completos = b""
    tentativas_sem_resposta = 0

    while True:
        try:
            pacote, addr = sock.recvfrom(9000)

            tentativas_sem_resposta = 0

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

        except socket.timeout:
            tentativas_sem_resposta += 1

            if len(dados_completos) > 0:
                print("Timeout aguardando novos pacotes. Finalizando recebimento.")
                break

            if tentativas_sem_resposta >= 3:
                raise TimeoutError("Servidor R-UDP nao respondeu.")

    return dados_completos


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


def requisicao_http_rudp(ip_servidor, caminho):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)

    addr_servidor = (ip_servidor, HTTP_RUDP_PORT)

    requisicao = (
        f"GET {caminho} HTTP/1.1\r\n"
        f"Host: {DOMINIO}\r\n"
        f"X-Custom-Auth: {AUTH}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )

    inicio = time.time()

    retransmissoes_envio = enviar_confiavel(
        client,
        addr_servidor,
        requisicao.encode()
    )

    try:
        resposta = receber_confiavel(client)
        sucesso = 1

    except TimeoutError as erro:
        print(erro)
        resposta = b""
        sucesso = 0

    fim = time.time()
    client.close()

    tempo_http = fim - inicio
    tamanho = len(resposta)

    if tempo_http > 0:
        throughput = tamanho / tempo_http / 1024
    else:
        throughput = 0

    if len(resposta) > 0:
        print("\nResposta HTTP recebida via R-UDP:")
        print(resposta[:300].decode(errors="ignore"))
    else:
        print("\nNenhuma resposta HTTP recebida via R-UDP.")

    print(f"\nTempo HTTP R-UDP: {tempo_http:.6f} segundos")
    print(f"Tamanho da resposta: {tamanho} bytes")
    print(f"Throughput: {throughput:.2f} KB/s")
    print(f"Retransmissões no envio da requisição: {retransmissoes_envio}")
    print(f"Sucesso: {sucesso}")

    return tempo_http, tamanho, throughput, retransmissoes_envio, sucesso


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python cliente_http_rudp.py /arquivo_100kb.bin A")
        exit()

    caminho = sys.argv[1]
    cenario = sys.argv[2]

    inicio_total = time.time()

    ip, tempo_dns = resolver_dns(DOMINIO)

    if ip is None or ip == "0.0.0.0":
        print("Nao foi possivel resolver o dominio.")

        with open("resultados_http_rudp.csv", "a") as arquivo:
            arquivo.write(
                f"{cenario},{caminho},{tempo_dns},0,{tempo_dns},0,0,0,0\n"
            )

        exit()

    tempo_http, tamanho, throughput, retransmissoes, sucesso = requisicao_http_rudp(
        ip,
        caminho
    )

    fim_total = time.time()
    tempo_total = fim_total - inicio_total

    with open("resultados_http_rudp.csv", "a") as arquivo:
        arquivo.write(
            f"{cenario},{caminho},{tempo_dns},{tempo_http},{tempo_total},{tamanho},{throughput},{retransmissoes},{sucesso}\n"
        )

    print(f"\nTempo total DNS + HTTP R-UDP: {tempo_total:.6f} segundos")