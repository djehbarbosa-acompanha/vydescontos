"""Lê a lista de ofertas do Mercado Livre (links gerados no painel de afiliados).

Arquivo data/mercadolivre.csv, separado por ponto e vírgula:
titulo;preco;desconto;imagem;link
"""
import csv, hashlib, os

def carregar(caminho="data/mercadolivre.csv"):
    if not os.path.exists(caminho):
        return []
    ofertas = []
    with open(caminho, encoding="utf-8") as f:
        for l in csv.DictReader(f, delimiter=";"):
            if not l.get("link"):
                continue
            ofertas.append({
                "loja": "Mercado Livre",
                "id": "ml-" + hashlib.md5(l["link"].encode()).hexdigest()[:12],
                "titulo": l["titulo"].strip(),
                "preco": float(l["preco"].replace(",", ".")),
                "desconto": int(l.get("desconto") or 0),
                "comissao": 0.0, "imagem": l["imagem"].strip(), "link": l["link"].strip(),
                "vendas": 0, "nota": 0.0,
            })
    return ofertas
