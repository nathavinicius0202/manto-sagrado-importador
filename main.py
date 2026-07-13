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


imagem = ""


if img:
    imagem = img.get("src") or img.get("data-src") or ""
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
def extrair_preco(texto):
    if not texto:
        return 0

    valores = re.findall(r'R\$\s?(\d+[.,]?\d*)', texto)

    if valores:
        valor = valores[-1]
        valor = valor.replace(".", "").replace(",", ".")
        return float(valor)

    return 0
@app.get("/importar")
def importar_catalogo():

    url = "https://xingestoque.com"

    try:

        resposta = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=10
        )

        resposta.raise_for_status()

    except Exception as erro:

        return {
            "erro": "Não foi possível acessar o catálogo.",
            "detalhes": str(erro)
        }

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    total = 0
    nomes = set()
    produtos = []

    for item in soup.find_all("a"):

        texto = item.get_text(
            " ",
            strip=True
        )

        if "Camisa" in texto and "R$" in texto:

            nome = limpar_nome(texto)

            imagem = ""

            img = item.find("img")

            if img:
                imagem = img.get("src") or img.get("data-src") or ""

            if nome in nomes:
                continue

            nomes.add(nome)

            preco_texto = texto.replace(nome, "")

            custo = extrair_preco(preco_texto)

            if custo > 0:

                venda, lucro = calcular_preco(custo)

                produtos.append((
                    nome,
                    "Camisa",
                    imagem,
                    custo,
                    venda,
                    lucro
                ))

                total += 1

    if total == 0:

        return {
            "erro": "Nenhum produto encontrado."
        }

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("DELETE FROM produtos")

    cursor.execute(
        "ALTER SEQUENCE produtos_id_seq RESTART WITH 1"
    )

    for produto in produtos:

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
        """, produto)

    banco.commit()
    banco.close()

    return {
        "mensagem": "Catálogo atualizado com sucesso.",
        "total_produtos": total
    }

@app.put("/produto/{id}")
def alterar_preco(id: int, custo: float):

    venda, lucro = calcular_preco(custo)

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
    UPDATE produtos
    SET custo=%s,
        preco_venda=%s,
        lucro=%s
    WHERE id=%s
    """, (
        custo,
        venda,
        lucro,
        id
    ))

    banco.commit()
    banco.close()

    return {
        "mensagem": "Preço atualizado",
        "id": id,
        "custo": custo,
        "preco_venda": venda,
        "lucro": lucro
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
    

   
