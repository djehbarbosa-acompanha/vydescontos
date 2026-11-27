"""Publica no Instagram (Reels do meio-dia + carrossel da noite) e no Pinterest.
Roda DEPOIS do push, porque artes e vídeos precisam estar públicos no GitHub."""
import json, os, sys, time, urllib.request
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(__file__))
import ig

BRT = timezone(timedelta(hours=-3))

def _brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def url_publica(caminho):
    return f"https://raw.githubusercontent.com/{os.environ['GITHUB_REPOSITORY']}/main/{caminho}"

def pinterest(rodada, cfg):
    token, board = os.environ.get("PINTEREST_TOKEN"), os.environ.get("PINTEREST_BOARD")
    if not (token and board):
        return
    for o in rodada["ofertas"]:
        try:
            req = urllib.request.Request("https://api.pinterest.com/v5/pins", method="POST",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                data=json.dumps({"board_id": board, "title": o["titulo"][:95], "link": o["links"]["pinterest"],
                    "description": f"{o['titulo'][:300]} por {_brl(o['preco'])}. {cfg['aviso_afiliado']}",
                    "media_source": {"source_type": "image_url", "url": url_publica(o["card"])}}).encode())
            urllib.request.urlopen(req, timeout=60).read()
            print("Pin criado:", o["titulo"][:50])
        except Exception as e:
            print("Erro Pinterest", e)

def _legenda(cfg, ofertas, titulo):
    linhas = [titulo, ""] + [f"{i}. {o['titulo'][:60]} – {_brl(o['preco'])}" + (f" ({o['desconto']}% OFF)" if o.get("desconto") else "")
                             for i, o in enumerate(ofertas, 1)]
    return "\n".join(linhas + ["", cfg["cta_comentario"], "🔗 Ou pegue no link do perfil.", "", cfg["aviso_afiliado"], "", cfg["hashtags"]])

def _aguardar(container):
    for _ in range(40):
        st = ig.get(container, fields="status_code").get("status_code")
        if st == "FINISHED": return
        if st in ("ERROR", "EXPIRED"): raise RuntimeError("container " + st)
        time.sleep(10)
    raise RuntimeError("tempo esgotado processando mídia")

def _do_dia(hist, data, n):
    hoje = [v for v in hist["vitrine"] if v.get("card") and v.get("data") == data]
    return sorted(hoje, key=lambda o: o.get("desconto", 0), reverse=True)[:n]

def reels(cfg, hist, agora):
    data = agora.date().isoformat(); video = f"docs/reels/{data}.mp4"
    if hist.get("ultimo_reels") == data or not os.path.exists(video):
        return
    ofertas = _do_dia(hist, data, cfg.get("reels_itens", 4))
    try:
        c = ig.post(f"{ig.conta()}/media", media_type="REELS", video_url=url_publica(video), share_to_feed="true",
                    caption=_legenda(cfg, ofertas, "🔥 " + cfg["instagram_chamada"]))["id"]
        _aguardar(c)
        mid = ig.post(f"{ig.conta()}/media_publish", creation_id=c)["id"]
        ig.registrar_post(mid, "reels", ofertas)
        hist["ultimo_reels"] = data
        print("Instagram: Reels publicado", mid)
    except Exception as e:
        print("Erro Reels", e)

def carrossel(cfg, hist, agora):
    data = agora.date().isoformat()
    if agora.hour < cfg["instagram_hora_minima"] or hist.get("ultimo_instagram") == data:
        return
    ofertas = _do_dia(hist, data, cfg["instagram_itens"])
    if len(ofertas) < 2:
        print("Instagram: poucas ofertas hoje."); return
    try:
        filhos = [ig.post(f"{ig.conta()}/media", image_url=url_publica(c), is_carousel_item="true")["id"]
                  for c in ["docs/cards/capa.jpg"] + [o["card"] for o in ofertas]]
        c = ig.post(f"{ig.conta()}/media", media_type="CAROUSEL", children=",".join(filhos),
                    caption=_legenda(cfg, ofertas, cfg["instagram_chamada"]))["id"]
        _aguardar(c)
        mid = ig.post(f"{ig.conta()}/media_publish", creation_id=c)["id"]
        ig.registrar_post(mid, "carrossel", ofertas)
        hist["ultimo_instagram"] = data
        print("Instagram: carrossel publicado com", len(ofertas), "ofertas")
    except Exception as e:
        print("Erro carrossel", e)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cfg = json.load(open("config.json", encoding="utf-8"))
    rodada = json.load(open("data/rodada.json", encoding="utf-8"))
    hist = json.load(open("data/historico.json"))
    pinterest(rodada, cfg)
    if os.environ.get("IG_TOKEN"):
        agora = datetime.now(BRT)
        reels(cfg, hist, agora)
        carrossel(cfg, hist, agora)
        json.dump(hist, open("data/historico.json", "w"), ensure_ascii=False, indent=1)
