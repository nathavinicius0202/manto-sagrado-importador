from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/")
def inicio():
    return FileResponse("index.html")

produtos = [
    {
        "id": 1,
        "nome": "Camisa Palmeiras I 2026/27",
        "preco": 149.90,
        "categoria": "Brasileirão"
    }
]

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
