from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="Manto Sagrado API",
    version="1.0.0"
)

@app.get("/")
def inicio():
    return {
        "mensagem": "Manto Sagrado funcionando!"
    }

@app.get("/status")
def status():
    return {
        "status": "online",
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "versao": "1.0.0"
    }
