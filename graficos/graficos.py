import pandas as pd
import matplotlib.pyplot as plt

tcpA = pd.read_csv("tcp_A.csv", names=["tempo", "throughput"])
tcpB = pd.read_csv("tcp_B.csv", names=["tempo", "throughput"])
tcpC = pd.read_csv("tcp_C.csv", names=["tempo", "throughput"])

rudpA = pd.read_csv("rudp_A.csv", names=["tempo", "throughput", "retransmissoes"])
rudpB = pd.read_csv("rudp_B.csv", names=["tempo", "throughput", "retransmissoes"])
rudpC = pd.read_csv("rudp_C.csv", names=["tempo", "throughput", "retransmissoes"])

cenarios = ["A", "B", "C"]

tcp_throughput = [
    tcpA["throughput"].mean(),
    tcpB["throughput"].mean(),
    tcpC["throughput"].mean()
]

rudp_throughput = [
    rudpA["throughput"].mean(),
    rudpB["throughput"].mean(),
    rudpC["throughput"].mean()
]

tcp_tempo = [
    tcpA["tempo"].mean(),
    tcpB["tempo"].mean(),
    tcpC["tempo"].mean()
]

rudp_tempo = [
    rudpA["tempo"].mean(),
    rudpB["tempo"].mean(),
    rudpC["tempo"].mean()
]

rudp_retransmissoes = [
    rudpA["retransmissoes"].mean(),
    rudpB["retransmissoes"].mean(),
    rudpC["retransmissoes"].mean()
]

print("\n===== ESTATÍSTICAS TCP =====")
for nome, dados in [("A", tcpA), ("B", tcpB), ("C", tcpC)]:
    print(f"\nCenário {nome}")
    print(f"Tempo médio: {dados['tempo'].mean():.6f} s")
    print(f"Throughput mínimo: {dados['throughput'].min():.2f} KB/s")
    print(f"Throughput médio: {dados['throughput'].mean():.2f} KB/s")
    print(f"Throughput máximo: {dados['throughput'].max():.2f} KB/s")
    print(f"Desvio padrão: {dados['throughput'].std():.2f}")

print("\n===== ESTATÍSTICAS RUDP =====")
for nome, dados in [("A", rudpA), ("B", rudpB), ("C", rudpC)]:
    print(f"\nCenário {nome}")
    print(f"Tempo médio: {dados['tempo'].mean():.6f} s")
    print(f"Throughput mínimo: {dados['throughput'].min():.2f} KB/s")
    print(f"Throughput médio: {dados['throughput'].mean():.2f} KB/s")
    print(f"Throughput máximo: {dados['throughput'].max():.2f} KB/s")
    print(f"Desvio padrão: {dados['throughput'].std():.2f}")
    print(f"Retransmissões médias: {dados['retransmissoes'].mean():.2f}")

plt.figure(figsize=(8, 5))
plt.plot(cenarios, tcp_throughput, marker="o", label="TCP")
plt.plot(cenarios, rudp_throughput, marker="o", label="RUDP")
plt.title("Throughput Médio - TCP vs RUDP")
plt.xlabel("Cenário")
plt.ylabel("KB/s")
plt.legend()
plt.savefig("throughput_tcp_vs_rudp.png")
plt.show()

plt.figure(figsize=(8, 5))
plt.plot(cenarios, rudp_throughput, marker="o")
plt.title("Throughput Médio - RUDP")
plt.xlabel("Cenário")
plt.ylabel("KB/s")
plt.savefig("throughput_rudp.png")
plt.show()

plt.figure(figsize=(8, 5))
plt.plot(cenarios, tcp_tempo, marker="o", label="TCP")
plt.plot(cenarios, rudp_tempo, marker="o", label="RUDP")
plt.title("Tempo Médio - TCP vs RUDP")
plt.xlabel("Cenário")
plt.ylabel("Segundos")
plt.legend()
plt.savefig("tempo_medio.png")
plt.show()

plt.figure(figsize=(8, 5))
plt.plot(cenarios, rudp_retransmissoes, marker="o")
plt.title("Retransmissões Médias - RUDP")
plt.xlabel("Cenário")
plt.ylabel("Retransmissões")
plt.savefig("retransmissoes_rudp.png")
plt.show()