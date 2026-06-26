import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PASTA_SCRIPT = Path(__file__).parent
PASTA_PROJETO = PASTA_SCRIPT.parent

ARQUIVOS = {
    ("TCP", "A"): PASTA_PROJETO / "http_tcp_A.csv",
    ("TCP", "B"): PASTA_PROJETO / "http_tcp_B.csv",
    ("TCP", "C"): PASTA_PROJETO / "http_tcp_C.csv",
    ("R-UDP", "A"): PASTA_PROJETO / "http_rudp_A.csv",
    ("R-UDP", "B"): PASTA_PROJETO / "http_rudp_B.csv",
    ("R-UDP", "C"): PASTA_PROJETO / "http_rudp_C.csv",
}

COLUNAS_TCP = [
    "cenario",
    "arquivo",
    "tempo_dns",
    "tempo_http",
    "tempo_total",
    "tamanho",
    "throughput",
]

COLUNAS_RUDP = [
    "cenario",
    "arquivo",
    "tempo_dns",
    "tempo_http",
    "tempo_total",
    "tamanho",
    "throughput",
    "retransmissoes",
    "sucesso",
]

def nome_tamanho(arquivo):
    if "100kb" in arquivo:
        return "100 KB"
    if "1mb" in arquivo:
        return "1 MB"
    if "5mb" in arquivo:
        return "5 MB"
    return arquivo


def carregar_dados():
    dados = []

    for (protocolo, cenario), caminho in ARQUIVOS.items():
        if not caminho.exists():
            print(f"Arquivo não encontrado: {caminho}")
            continue

        if protocolo == "TCP":
            df = pd.read_csv(caminho, names=COLUNAS_TCP)
            df["retransmissoes"] = 0
            df["sucesso"] = 1
        else:
            df = pd.read_csv(caminho, names=COLUNAS_RUDP)

        df["protocolo"] = protocolo
        df["cenario"] = cenario
        df["tamanho_nome"] = df["arquivo"].apply(nome_tamanho)

        dados.append(df)

    if not dados:
        raise Exception("Nenhum CSV foi carregado.")

    return pd.concat(dados, ignore_index=True)


df = carregar_dados()

ordem_cenarios = ["A", "B", "C"]
ordem_tamanhos = ["100 KB", "1 MB", "5 MB"]

estatisticas = (
    df.groupby(["protocolo", "cenario", "tamanho_nome"])
    .agg(
        execucoes=("throughput", "count"),
        tempo_dns_medio=("tempo_dns", "mean"),
        tempo_http_medio=("tempo_http", "mean"),
        tempo_total_medio=("tempo_total", "mean"),
        throughput_minimo=("throughput", "min"),
        throughput_medio=("throughput", "mean"),
        throughput_maximo=("throughput", "max"),
        throughput_desvio=("throughput", "std"),
        retransmissoes_media=("retransmissoes", "mean"),
        sucesso_medio=("sucesso", "mean"),
    )
    .reset_index()
)

estatisticas.to_csv(PASTA_SCRIPT / "tabela_estatisticas.csv", index=False)

print("\n===== TABELA DE ESTATÍSTICAS =====")
print(estatisticas.to_string(index=False))

# Gráfico 1: Throughput médio TCP vs R-UDP por cenário

media_cenario = (
    df.groupby(["protocolo", "cenario"])["throughput"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(8, 5))

for protocolo in ["TCP", "R-UDP"]:
    dados = media_cenario[media_cenario["protocolo"] == protocolo]
    dados = dados.set_index("cenario").reindex(ordem_cenarios).reset_index()

    plt.plot(
        dados["cenario"],
        dados["throughput"],
        marker="o",
        label=protocolo
    )

plt.title("Throughput Médio com DNS - TCP vs R-UDP")
plt.xlabel("Cenário")
plt.ylabel("Throughput (KB/s)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(PASTA_SCRIPT / "grafico_throughput_tcp_rudp.png")
plt.show()

# Gráfico 2: Tempo total médio TCP vs R-UDP por cenário

tempo_cenario = (
    df.groupby(["protocolo", "cenario"])["tempo_total"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(8, 5))

for protocolo in ["TCP", "R-UDP"]:
    dados = tempo_cenario[tempo_cenario["protocolo"] == protocolo]
    dados = dados.set_index("cenario").reindex(ordem_cenarios).reset_index()

    plt.plot(
        dados["cenario"],
        dados["tempo_total"],
        marker="o",
        label=protocolo
    )

plt.title("Tempo Total Médio DNS + HTTP")
plt.xlabel("Cenário")
plt.ylabel("Tempo total (s)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(PASTA_SCRIPT / "grafico_tempo_total_tcp_rudp.png")
plt.show()

# Gráfico 3: Tempo médio DNS por cenário

dns_cenario = (
    df.groupby("cenario")["tempo_dns"]
    .mean()
    .reindex(ordem_cenarios)
    .reset_index()
)

plt.figure(figsize=(8, 5))
plt.plot(
    dns_cenario["cenario"],
    dns_cenario["tempo_dns"],
    marker="o"
)

plt.title("Tempo Médio de Resolução DNS por Cenário")
plt.xlabel("Cenário")
plt.ylabel("Tempo DNS (s)")
plt.grid(True)
plt.tight_layout()
plt.savefig(PASTA_SCRIPT / "grafico_dns_por_cenario.png")
plt.show()

# Gráfico 4: Throughput por tamanho de arquivo e protocolo

media_tamanho = (
    df.groupby(["protocolo", "tamanho_nome"])["throughput"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(8, 5))

for protocolo in ["TCP", "R-UDP"]:
    dados = media_tamanho[media_tamanho["protocolo"] == protocolo]
    dados = dados.set_index("tamanho_nome").reindex(ordem_tamanhos).reset_index()

    plt.plot(
        dados["tamanho_nome"],
        dados["throughput"],
        marker="o",
        label=protocolo
    )

plt.title("Throughput Médio por Tamanho de Arquivo")
plt.xlabel("Tamanho do arquivo")
plt.ylabel("Throughput (KB/s)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(PASTA_SCRIPT / "grafico_por_tamanho_arquivo.png")
plt.show()

# Gráfico 5: Retransmissões médias do R-UDP por cenário

rudp = df[df["protocolo"] == "R-UDP"]

retrans_cenario = (
    rudp.groupby("cenario")["retransmissoes"]
    .mean()
    .reindex(ordem_cenarios)
    .reset_index()
)

plt.figure(figsize=(8, 5))
plt.plot(
    retrans_cenario["cenario"],
    retrans_cenario["retransmissoes"],
    marker="o"
)

plt.title("Retransmissões Médias no R-UDP por Cenário")
plt.xlabel("Cenário")
plt.ylabel("Retransmissões médias")
plt.grid(True)
plt.tight_layout()
plt.savefig(PASTA_SCRIPT / "grafico_retransmissoes_rudp.png")
plt.show()

# Gráfico 6: Taxa de sucesso do R-UDP

sucesso_cenario = (
    rudp.groupby("cenario")["sucesso"]
    .mean()
    .reindex(ordem_cenarios)
    .reset_index()
)

sucesso_cenario["sucesso_percentual"] = sucesso_cenario["sucesso"] * 100

plt.figure(figsize=(8, 5))
plt.plot(
    sucesso_cenario["cenario"],
    sucesso_cenario["sucesso_percentual"],
    marker="o"
)

plt.title("Taxa de Sucesso do R-UDP por Cenário")
plt.xlabel("Cenário")
plt.ylabel("Sucesso (%)")
plt.ylim(0, 105)
plt.grid(True)
plt.tight_layout()
plt.savefig(PASTA_SCRIPT / "grafico_sucesso_rudp.png")
plt.show()

print("\nArquivos gerados na pasta 'graficos':")
print("grafico_throughput_tcp_rudp.png")
print("grafico_tempo_total_tcp_rudp.png")
print("grafico_dns_por_cenario.png")
print("grafico_por_tamanho_arquivo.png")
print("grafico_retransmissoes_rudp.png")
print("grafico_sucesso_rudp.png")
print("tabela_estatisticas.csv")