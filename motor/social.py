"""Publica no Instagram (carrossel diário) e no Pinterest (um pin por oferta).
Roda DEPOIS do push, porque as artes precisam estar públicas no GitHub."""
import json, os, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

BRT = timezone(timedelta(hours=-3))
GRAPH = "https://graph.facebook.com/v21.0"

def _post(url, campos, headers=None, json_body=None):
    if json_body is not None:
        dados = json.dumps(json_body).encode(); headers = {**(headers or {}), "Content-Type": "application/json"}
    else:
        dados = urllib.parse.urlencode(campos).encode()
    req = urllib.request.Request(url, data=dados, headers=headers or {}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def _brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def url_publica(caminho):
    repo = os.environ["GITHUB_REPOSITORY"]
    return f"https://raw.githubusercontent.com/{repo}/main/{caminho}"

def pinterest(rodada, cfg):
    token, board = os.environ.get("PINTEREST_TOKEN"), os.environ.get("PINTEREST_BOARD")
    if not (token and board):
        return
    for o in rodada["ofertas"]:
        try:
            _post("https://api.pinterest.com/v5/pins", None, {"Authorization": f"Bearer {token}"}, {
                "board_id": board, "title": o["titulo"][:95], "link": o["links"]["pinterest"],
                "description": f"{o['titulo'][:300]} por {_brl(o['preco'])}. {cfg['aviso_afiliado']}",
                "media_source": {"source_type": "image_url", "url": url_publica(o["card"])}})
            print("Pin criado:", o["titulo"][:50])
        except Exception as e:
            print("Erro Pinterest", e)

def instagram(cfg):
    token, conta = os.environ.get("IG_TOKEN"), os.environ.get("IG_USER_ID")
    agora = datetime.now(BRT)
    if not (token and conta) or agora.hour < cfg["instagram_hora_minima"]:
        return
    hist = json.load(open("data/historico.json"))
    if hist.get("ultimo_instagram") == agora.date().isoformat():
        return
    hoje = [v for v in hist["vitrine"] if v.get("card") and v.get("data", "").startswith(agora.date().isoformat())]
    hoje = sorted(hoje, key=lambda o: o.get("desconto", 0), reverse=True)[:cfg["instagram_itens"]]
    if len(hoje) < 2:
        print("Instagram: poucas ofertas hoje, pulando."); return
    try:
        filhos = []
        for c in ["docs/cards/capa.jpg"] + [o["card"] for o in hoje]:
            r = _post(f"{GRAPH}/{conta}/media", {"image_url": url_publica(c), "is_carousel_item": "true", "access_token": token})
            filhos.append(r["id"])
        linhas = [cfg["instagram_chamada"], ""] + [f"{i}. {o['titulo'][:60]} – {_brl(o['preco'])}" + (f" ({o['desconto']}% OFF)" if o.get("desconto") else "") for i, o in enumerate(hoje, 1)]
        legenda = "\n".join(linhas + ["", "🔗 Links no perfil (site) e no nosso canal.", "", cfg["aviso_afiliado"], "", cfg["hashtags"]])
        r = _post(f"{GRAPH}/{conta}/media", {"media_type": "CAROUSEL", "children": ",".join(filhos), "caption": legenda, "access_token": token})
        time.sleep(15)
        _post(f"{GRAPH}/{conta}/media_publish", {"creation_id": r["id"], "access_token": token})
        hist["ultimo_instagram"] = agora.date().isoformat()
        json.dump(hist, open("data/historico.json", "w"), ensure_ascii=False, indent=1)
        print("Instagram: carrossel publicado com", len(hoje), "ofertas")
    except Exception as e:
        print("Erro Instagram", e)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cfg = json.load(open("config.json", encoding="utf-8"))
    rodada = json.load(open("data/rodada.json", encoding="utf-8"))
    pinterest(rodada, cfg)
    instagram(cfg)
