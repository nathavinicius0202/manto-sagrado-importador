from fastapi import FastAPI
from fastapi.responses import FileResponse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

app = FastAPI()

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

    venda = custo + (custo * margem)
    lucro = venda - custo

    return round(venda, 2), round(lucro, 2)


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


@app.get("/importar")
def importar_catalogo():

    url = "https://xingestoque.com"

    try:

        resposta = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        soup = BeautifulSoup(
            resposta.text,
            "html.parser"
        )

        encontrados = []

        textos = soup.find_all("a")

        for item in textos:

            nome = item.get_text(
                strip=True
            )

            if "Camisa" in nome:

                encontrados.append({
                    "nome": nome,
                    "categoria": "Camisa"
                })


        return {
            "mensagem": "Busca concluída",
            "produtos_encontrados": len(encontrados),
            "dados": encontrados[:10]
        }


    except Exception as erro:

        return {
            "erro": str(erro)
        }


@app.get("/config")
def ver_config():
    return config


@app.post("/config/margem/{valor}")
def alterar_margem(valor: float):

    config["margem"] = valor

    return {
        "mensagem": "Margem atualizada",
        "margem": valor
    }


@app.get("/lucro")
def resumo_lucro():

    investimento = sum(p["custo"] for p in produtos)
    faturamento = sum(p["preco_venda"] for p in produtos)
    lucro = sum(p["lucro"] for p in produtos)

    return {
        "investimento": investimento,
        "faturamento": faturamento,
        "lucro": lucro
    }
