"""Chamadas à API do Instagram. Funciona com token do 'Login do Instagram' (começa com IG)
ou do 'Login do Facebook' (conta ligada a uma Página)."""
import json, os, urllib.parse, urllib.request

def base():
    t = os.environ.get("IG_TOKEN", "")
    return "https://graph.instagram.com/v21.0" if t.startswith("IG") else "https://graph.facebook.com/v21.0"

def _req(metodo, caminho, campos=None, corpo=None):
    campos = dict(campos or {}); campos["access_token"] = os.environ["IG_TOKEN"]
    url = f"{base()}/{caminho}"
    if metodo == "GET":
        req = urllib.request.Request(url + "?" + urllib.parse.urlencode(campos))
    elif corpo is not None:
        req = urllib.request.Request(url + "?access_token=" + campos["access_token"], data=json.dumps(corpo).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
    else:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(campos).encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode()[:400]}")

def get(caminho, **campos): return _req("GET", caminho, campos)
def post(caminho, **campos): return _req("POST", caminho, campos)
def post_json(caminho, corpo): return _req("POST", caminho, corpo=corpo)

def conta(): return os.environ.get("IG_USER_ID") or "me"

POSTS = "data/posts_ig.json"
def registrar_post(media_id, tipo, ofertas):
    d = json.load(open(POSTS)) if os.path.exists(POSTS) else {}
    from datetime import datetime, timezone
    d[media_id] = {"tipo": tipo, "data": datetime.now(timezone.utc).isoformat(),
                   "ofertas": [{"titulo": o["titulo"][:70], "preco": o["preco"], "link": o["links"]["instagram"]} for o in ofertas]}
    d = dict(sorted(d.items(), key=lambda kv: kv[1]["data"], reverse=True)[:40])
    json.dump(d, open(POSTS, "w"), ensure_ascii=False, indent=1)
