#!/usr/bin/env python3
"""Testa se a chave xAI voltou a ter credito. Nao mexe no bot."""
import os, httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
key = os.getenv("XAI_API_KEY")
if not key:
    raise SystemExit("XAI_API_KEY nao encontrada no .env")

try:
    r = httpx.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": "grok-3-mini",
              "messages": [{"role": "user", "content": "responda apenas: ok"}],
              "max_tokens": 20},
        timeout=30,
    )
    data = r.json()
except Exception as e:
    raise SystemExit(f"FALHA de conexao: {e}")

if "choices" in data:
    print("CREDITO OK -> a Pastora ja esta gerando respostas normalmente.")
    print("Resposta do Grok:", data["choices"][0]["message"]["content"].strip())
else:
    print("AINDA SEM CREDITO -> ela segue respondendo so as frases fixas.")
    print("Erro:", data.get("error", data))
