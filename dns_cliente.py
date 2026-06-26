import socket
import random
import time

DNS_SERVER = "172.30.0.53"
DNS_PORT = 5353

DOMINIO = "www.meusite.local"

def resolver_nome(nome):
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

        partes = resposta.split(";")

        ip = None

        for parte in partes:
            if parte.startswith("IP="):
                ip = parte.replace("IP=", "")

        tempo_dns = fim - inicio

        print("Consulta DNS enviada:")
        print(mensagem)

        print("\nResposta DNS recebida:")
        print(resposta)

        print(f"\nIP resolvido: {ip}")
        print(f"Tempo de resolução DNS: {tempo_dns:.6f} segundos")

        client.close()

        return ip, tempo_dns

    except socket.timeout:
        fim = time.time()

        print("Timeout na resolução DNS.")

        client.close()

        return None, fim - inicio


if __name__ == "__main__":
    resolver_nome(DOMINIO)