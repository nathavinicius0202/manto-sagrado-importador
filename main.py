from fastapi import FastAPI
from fastapi.responses import FileResponse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

config = {
    "margem": 100
}

produtos = []


def calcular_preco(custo):
    margem = config["margem"] / 100

    venda = custo + (custo * margem)
    lucro = venda - custo

    return round(venda, 2), round(lucro, 2)


def limpar_nome(texto):

    texto = re.sub(
        r"Até.*",
        "",
        texto
    )

    texto = re.sub(
        r"Comprar.*",
        "",
        texto
    )

    return texto.strip()


def extrair_preco(texto):

    valores = re.findall(
        r"R\$ ?(\d+,\d+)",
        texto
    )

    if valores:
        return float(
            valores[0].replace(",", ".")
        )

    return 0


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

    global produtos

    url = "https://xingestoque.com"

    resposta = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=15
    )

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    novos_produtos = []

    links = soup.find_all("a")


    for item in links:

        texto = item.get_text(
            " ",
            strip=True
        )

        if "Camisa" in texto and "R$" in texto:

            nome = limpar_nome(texto)

            custo = extrair_preco(texto)


            if custo > 0:

                venda, lucro = calcular_preco(custo)

                novos_produtos.append({

                    "id": len(novos_produtos)+1,
                    "nome": nome,
                    "categoria": "Camisa",
                    "custo": custo,
                    "preco_venda": venda,
                    "lucro": lucro

                })


    produtos = novos_produtos


    return {

        "mensagem": "Catálogo atualizado",
        "total_produtos": len(produtos)

    }


@app.get("/lucro")
def resumo_lucro():

    return {

        "investimento": sum(p["custo"] for p in produtos),
        "faturamento": sum(p["preco_venda"] for p in produtos),
        "lucro": sum(p["lucro"] for p in produtos)

    }


@app.get("/config")
def ver_config():
    return config


@app.post("/config/margem/{valor}")
def alterar_margem(valor: float):

    config["margem"] = valor

    return {
        "mensagem": "Margem alterada",
        "margem": valor
    }
