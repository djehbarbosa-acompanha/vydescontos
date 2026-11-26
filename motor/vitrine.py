"""Gera a vitrine de ofertas (docs/index.html), publicada pelo GitHub Pages."""
import html, json
from datetime import datetime, timezone, timedelta

BRT = timezone(timedelta(hours=-3))

def _brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar(ofertas, cfg, caminho="docs/index.html"):
    cards = []
    for o in ofertas[:60]:
        selo = f'<span class="off">-{o["desconto"]}%</span>' if o.get("desconto") else ""
        cards.append(f'''<a class="card" href="{html.escape(o.get("link_vitrine", o["link"]))}" target="_blank" rel="nofollow sponsored noopener">
  <div class="img"><img loading="lazy" src="{html.escape(o["imagem"])}" alt="">{selo}</div>
  <div class="info"><span class="loja {"ml" if o["loja"]!="Shopee" else ""}">{o["loja"]}</span>
  <p class="tit">{html.escape(o["titulo"][:90])}</p>
  <p class="preco">{_brl(o["preco"])}</p><span class="btn">Ver oferta</span></div></a>''')
    agora = datetime.now(BRT).strftime("%d/%m/%Y às %H:%M")
    pagina = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(cfg["marca"])}</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#faf7f2;color:#2b2b2b}}
header{{background:#1f3b2d;color:#fff;padding:28px 18px;text-align:center}}header h1{{margin:0;font-size:26px}}header p{{margin:6px 0 0;opacity:.85}}
.wrap{{max-width:1100px;margin:auto;padding:18px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:14px}}
.card{{background:#fff;border-radius:12px;overflow:hidden;text-decoration:none;color:inherit;box-shadow:0 1px 4px #0001;display:flex;flex-direction:column}}
.img{{position:relative;aspect-ratio:1;background:#eee}}.img img{{width:100%;height:100%;object-fit:cover}}
.off{{position:absolute;top:8px;left:8px;background:#e4572e;color:#fff;font-weight:700;font-size:13px;padding:3px 7px;border-radius:6px}}
.info{{padding:10px;display:flex;flex-direction:column;gap:4px;flex:1}}.loja{{font-size:11px;color:#ee4d2d;font-weight:700}}.loja.ml{{color:#2d3277}}
.tit{{font-size:13px;margin:0;line-height:1.3;flex:1}}.preco{{font-size:17px;font-weight:800;margin:4px 0}}
.btn{{background:#c9a44c;color:#fff;text-align:center;border-radius:8px;padding:7px;font-size:13px;font-weight:600}}
footer{{text-align:center;font-size:12px;color:#777;padding:24px}}
</style></head><body><header><h1>{html.escape(cfg["marca"])}</h1><p>{html.escape(cfg["slogan"])}</p></header>
<div class="wrap"><div class="grid">{"".join(cards)}</div></div>
<footer>Atualizado em {agora}. {html.escape(cfg["aviso_afiliado"])} Preços e estoque podem mudar a qualquer momento.</footer></body></html>'''
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(pagina)
