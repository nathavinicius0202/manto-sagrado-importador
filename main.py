from fastapi import FastAPI
from fastapi.responses import FileResponse
from datetime import datetime

app = FastAPI()

# Configuração da margem de lucro (%)
config = {
    "margem": 100
}

produtos = [
    {
        "id": 1,
        "nome": "Camisa Palmeiras I 2026/27",
        "categoria": "Brasileirão",
        "custo": 70.00,
        "preco_venda": 140.00,
        "lucro": 70.00
    }
]


def calcular_preco(custo):
    margem = config["margem"] / 100

    preco_venda = custo + (custo * margem)
    lucro = preco_venda - custo

    return round(preco_venda, 2), round(lucro, 2)


@app.get("/")
def inicio():
    return FileResponse("index.html")


@app.get("/status")
def status():
    return {
        "status": "online",
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "produtos": len(produtos)
    }


@app.get("/produtos")
def listar_produtos():
    return produtos


@app.get("/config")
def ver_config():
    return config


@app.post("/config/margem/{valor}")
def alterar_margem(valor: float):

    config["margem"] = valor

    return {
        "mensagem": "Margem atualizada",
        "nova_margem": valor
    }


@app.get("/lucro")
def resumo_lucro():

    investimento = sum(p["custo"] for p in produtos)
    faturamento = sum(p["preco_venda"] for p in produtos)
    lucro_total = sum(p["lucro"] for p in produtos)

    return {
        "investimento": round(investimento,2),
        "faturamento": round(faturamento,2),
        "lucro": round(lucro_total,2)
    }
