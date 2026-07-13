from fastapi import FastAPI
from fastapi.responses import FileResponse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import os
import psycopg2

app = FastAPI()

config = {
    "margem": 100
}


def conectar():
    return psycopg2.connect(
        os.environ["DATABASE_URL"]
    )


def criar_tabela():

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id SERIAL PRIMARY KEY,
        nome TEXT,
        categoria TEXT,
        imagem TEXT,
        custo REAL,
        preco_venda REAL,
        lucro REAL
    )
    """)

    banco.commit()
    banco.close()


criar_tabela()


def calcular_preco(custo):

    venda = custo + (custo * config["margem"] / 100)
    lucro = venda - custo

    return round(venda, 2), round(lucro, 2)


def limpar_nome(texto):

    texto = re.sub(r"Até.*", "", texto)
    texto = re.sub(r"Comprar.*", "", texto)

    return texto.strip()


@app.get("/")
def inicio():
    return FileResponse("index.html")


@app.get("/status")
def status():

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM produtos"
    )

    total = cursor.fetchone()[0]

    banco.close()

    return {
        "status": "online",
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "produtos": total
    }


@app.get("/produtos")
def listar_produtos():

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
    SELECT id,nome,categoria,imagem,custo,preco_venda,lucro
    FROM produtos
    ORDER BY id
    """)

    dados = cursor.fetchall()

    banco.close()

    lista = []

    for produto in dados:

        lista.append({
            "id": produto[0],
            "nome": produto[1],
            "categoria": produto[2],
            "imagem": produto[3],
            "custo": produto[4],
            "preco_venda": produto[5],
            "lucro": produto[6]
        })

    return lista
    @app.get("/importar")
def importar_catalogo():

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("DELETE FROM produtos")

    cursor.execute(
        "ALTER SEQUENCE produtos_id_seq RESTART WITH 1"
    )

    url = "https://xingestoque.com"

    resposta = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20
    )

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    total = 0
    nomes = set()

    for item in soup.find_all("a"):

        texto = item.get_text(
            " ",
            strip=True
        )

        if "Camisa" in texto and "R$" in texto:

            nome = limpar_nome(texto)

            if nome in nomes:
                continue

            nomes.add(nome)

            custo = extrair_preco(texto)

            if custo > 0:

                venda, lucro = calcular_preco(custo)

                cursor.execute("""
                INSERT INTO produtos
                (
                nome,
                categoria,
                imagem,
                custo,
                preco_venda,
                lucro
                )
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (
                nome,
                "Camisa",
                "",
                custo,
                venda,
                lucro
                ))

                total += 1

    banco.commit()
    banco.close()

    return {
        "mensagem": "Catálogo atualizado",
        "total_produtos": total
    }


@app.get("/lucro")
def lucro():

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
    SELECT
    SUM(custo),
    SUM(preco_venda),
    SUM(lucro)
    FROM produtos
    """)

    dados = cursor.fetchone()

    banco.close()

    return {
        "investimento": dados[0] or 0,
        "faturamento": dados[1] or 0,
        "lucro": dados[2] or 0
    }

   
