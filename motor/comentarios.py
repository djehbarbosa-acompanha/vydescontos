"""Robô 'Comenta LINK': lê os comentários dos posts do motor e manda os links no direct
(resposta privada oficial da Meta) + uma resposta curta no comentário. Roda a cada 15 min."""
import json, os, random, sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(__file__))
import ig

def _brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _gatilho(txt, palavras):
    t = (txt or "").lower()
    return any(p in t for p in palavras)

def mensagem(post, cfg):
    linhas = ["Oi! Aqui estão os links dos achados 👇", ""]
    for i, o in enumerate(post["ofertas"], 1):
        linhas += [f"{i}. {o['titulo']} – {_brl(o['preco'])}", o["link"], ""]
    linhas += ["Os preços mudam rápido, então aproveita! 😉", cfg["aviso_afiliado"]]
    return "\n".join(linhas)[:990]

def rodar():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.environ.get("IG_TOKEN") or not os.path.exists(ig.POSTS):
        print("Sem token ou sem posts ainda."); return
    cfg = json.load(open("config.json", encoding="utf-8"))
    posts = json.load(open(ig.POSTS))
    ARQ = "data/comentarios.json"
    feitos = json.load(open(ARQ)) if os.path.exists(ARQ) else {}
    eu = ig.get("me", fields="id,username")
    limite = datetime.now(timezone.utc) - timedelta(days=6)
    enviados = 0
    for mid, post in posts.items():
        if datetime.fromisoformat(post["data"]) < limite:
            continue
        try:
            coms = ig.get(f"{mid}/comments", fields="id,text,username,timestamp", limit=50).get("data", [])
        except Exception as e:
            print("Erro lendo comentários", mid, e); continue
        for c in coms:
            if c["id"] in feitos or c.get("username") == eu.get("username") or not _gatilho(c.get("text"), cfg["palavras_gatilho"]):
                continue
            try:
                ig.post_json(f"{ig.conta()}/messages", {"recipient": {"comment_id": c["id"]}, "message": {"text": mensagem(post, cfg)}})
                try:
                    ig.post(f"{c['id']}/replies", message=random.choice(cfg["resposta_publica"]))
                except Exception as e:
                    print("Resposta pública falhou", e)
                feitos[c["id"]] = datetime.now(timezone.utc).isoformat(); enviados += 1
                print("Direct enviado para", c.get("username"))
            except Exception as e:
                print("Erro direct", c.get("username"), e)
                feitos[c["id"]] = "erro"
    feitos = dict(list(feitos.items())[-2000:])
    json.dump(feitos, open(ARQ, "w"), indent=0)
    print("Directs enviados nesta rodada:", enviados)

if __name__ == "__main__":
    rodar()
