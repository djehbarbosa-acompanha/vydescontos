"""Publica ofertas no canal do Telegram pelo robô oficial (Bot API)."""
import html, json, os, urllib.parse, urllib.request

def _brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def legenda(o, aviso):
    t = html.escape(o["titulo"][:120])
    linhas = [f"🔥 <b>{t}</b>", ""]
    if o.get("desconto"):
        linhas.append(f"💸 <b>{o['desconto']}% OFF</b>")
    linhas.append(f"💰 Por <b>{_brl(o['preco'])}</b>")
    if o.get("nota"):
        linhas.append(f"⭐ {o['nota']:.1f}" + (f" · {o['vendas']}+ vendidos" if o.get("vendas") else ""))
    linhas += ["", f"🛒 <a href=\"{o.get('links',{}).get('telegram', o['link'])}\">Comprar na {o['loja']}</a>", "", f"<i>{html.escape(aviso)}</i>"]
    return "\n".join(linhas)

def publicar(o, aviso):
    token = os.environ["TELEGRAM_TOKEN"]; canal = os.environ["TELEGRAM_CANAL"]
    dados = urllib.parse.urlencode({
        "chat_id": canal, "photo": o["imagem"], "caption": legenda(o, aviso), "parse_mode": "HTML",
    }).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendPhoto", data=dados)
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    if not res.get("ok"):
        raise RuntimeError(res)


def resumo_para_mim(ofertas, campanha=None):
    """Manda para o SEU Telegram as ofertas já em texto de WhatsApp, prontas para copiar e colar."""
    token = os.environ.get("TELEGRAM_TOKEN"); chat = os.environ.get("TELEGRAM_MEU_CHAT")
    if not (token and chat and ofertas):
        return
    partes = []
    for o in ofertas:
        linha = [f"*{o['titulo'][:90]}*"]
        if o.get("desconto"):
            linha.append(f"🔥 {o['desconto']}% OFF")
        linha.append(f"💰 {_brl(o['preco'])}")
        linha.append(f"👉 {o.get('links',{}).get('whatsapp', o['link'])}")
        partes.append("\n".join(linha))
    topo = f"📲 Ofertas para o WhatsApp/stories" + (f" · {campanha}" if campanha else "") + "\n(copie cada bloco)\n\n"
    texto = topo + "\n\n———\n\n".join(partes)
    dados = urllib.parse.urlencode({"chat_id": chat, "text": texto[:4000], "disable_web_page_preview": "true"}).encode()
    urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=dados), timeout=30)
