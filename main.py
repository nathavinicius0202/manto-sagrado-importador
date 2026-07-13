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

    margem = config["margem"] / 100

    venda = custo + (custo * margem)

    lucro = venda - custo

    return round(venda,2), round(lucro,2)



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

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM produtos"
    )

    total = cursor.fetchone()[0]

    banco.close()


    return {

        "status":"online",

        "ultima_atualizacao":
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),

        "produtos":total

    }
    @app.get("/produtos")
def listar_produtos():

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
    SELECT id,nome,categoria,imagem,
    custo,preco_venda,lucro
    FROM produtos
    ORDER BY id
    """)

    dados = cursor.fetchall()

    banco.close()

    lista = []

    for p in dados:

        lista.append({

            "id": p[0],
            "nome": p[1],
            "categoria": p[2],
            "imagem": p[3],
            "custo": p[4],
            "preco_venda": p[5],
            "lucro": p[6]

        })

    return lista



@app.get("/importar")
def importar_catalogo():

    banco = conectar()
    cursor = banco.cursor()


    # apaga catálogo antigo
    cursor.execute(
        "DELETE FROM produtos"
    )


    # reinicia contador de ID
    cursor.execute(
        "ALTER SEQUENCE produtos_id_seq RESTART WITH 1"
    )


    url = "https://xingestoque.com"


    resposta = requests.get(

        url,

        headers={
            "User-Agent":"Mozilla/5.0"
        },

        timeout=20

    )


    soup = BeautifulSoup(

        resposta.text,

        "html.parser"

    )


    total = 0

    nomes_salvos = set()



    for item in soup.find_all("a"):


        texto = item.get_text(
            " ",
            strip=True
        )


        if "Camisa" in texto and "R$" in texto:


            nome = limpar_nome(texto)


            # remove duplicados
            if nome in nomes_salvos:
                continue


            nomes_salvos.add(nome)


            custo = extrair_preco(texto)


            imagem = ""


            foto = item.find("img")

            if foto:

                imagem = foto.get("src")



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
                imagem,
                custo,
                venda,
                lucro

                ))


                total += 1



    banco.commit()

    banco.close()


    return {

        "mensagem":
        "Catálogo atualizado sem duplicados",

        "total_produtos":
        total

    }



@app.get("/lucro")
def resumo_lucro():

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
