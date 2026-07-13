from fastapi import FastAPI
from fastapi.responses import FileResponse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import sqlite3

app = FastAPI()

config = {
    "margem": 100
}


# Criar banco
def conectar():

    return sqlite3.connect("produtos.db")


def criar_tabela():

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        categoria TEXT,
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

    total = banco.execute(
        "SELECT COUNT(*) FROM produtos"
    ).fetchone()[0]

    banco.close()


    return {

        "status":"online",

        "ultima_atualizacao":
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),

        "produtos": total

    }



@app.get("/produtos")
def listar_produtos():

    banco = conectar()

    dados = banco.execute(
        "SELECT * FROM produtos"
    ).fetchall()

    banco.close()


    lista=[]

    for p in dados:

        lista.append({

            "id":p[0],
            "nome":p[1],
            "categoria":p[2],
            "custo":p[3],
            "preco_venda":p[4],
            "lucro":p[5]

        })


    return lista




@app.get("/importar")
def importar_catalogo():

    banco = conectar()

    cursor = banco.cursor()


    # limpa catálogo antigo
    cursor.execute(
        "DELETE FROM produtos"
    )


    url="https://xingestoque.com"


    resposta=requests.get(
        url,
        headers={
            "User-Agent":"Mozilla/5.0"
        },
        timeout=15
    )


    soup=BeautifulSoup(
        resposta.text,
        "html.parser"
    )


    total=0


    for item in soup.find_all("a"):


        texto=item.get_text(
            " ",
            strip=True
        )


        if "Camisa" in texto and "R$" in texto:


            nome=limpar_nome(texto)

            custo=extrair_preco(texto)


            if custo>0:


                venda,lucro=calcular_preco(custo)


                cursor.execute("""

                INSERT INTO produtos

                (nome,categoria,custo,preco_venda,lucro)

                VALUES (?,?,?,?,?)

                """,

                (

                nome,
                "Camisa",
                custo,
                venda,
                lucro

                ))


                total+=1



    banco.commit()

    banco.close()


    return {

        "mensagem":
        "Catálogo salvo com sucesso",

        "total_produtos":
        total

    }



@app.get("/lucro")
def lucro():

    banco=conectar()


    dados=banco.execute("""

    SELECT 
    SUM(custo),
    SUM(preco_venda),
    SUM(lucro)

    FROM produtos

    """).fetchone()


    banco.close()


    return {

        "investimento":dados[0] or 0,

        "faturamento":dados[1] or 0,

        "lucro":dados[2] or 0

    }
