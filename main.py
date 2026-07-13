from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="Manto Sagrado API",
    version="1.0.0"
)

# Banco temporário em memória
produtos = []

@app.get("/")
def inicio():
    return {"mensagem": "Manto Sagrado funcionando!"}

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

@app.post("/produto-teste")
def criar_produto():
    produto = {
        "id": 1,
        "nome": "Camisa Palmeiras I 2026/27",
        "preco": 149.90,
        "categoria": "Brasileirão"
    }
    produtos.append(produto)
    return {"mensagem": "Produto adicionado", "produto": produto}
