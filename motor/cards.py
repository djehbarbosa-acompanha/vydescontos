"""Cria as artes das ofertas (JPEG 1080x1350) para Instagram e Pinterest."""
import io, os, textwrap, urllib.request
from PIL import Image, ImageDraw, ImageFont

FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONTE_N = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
VERDE, DOURADO, CREME, LARANJA = (31, 59, 45), (201, 164, 76), (250, 247, 242), (228, 87, 46)

def _f(tam, negrito=True):
    try:
        return ImageFont.truetype(FONTE if negrito else FONTE_N, tam)
    except OSError:
        return ImageFont.load_default()

def _brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _foto(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")

def card(o, marca, caminho, rodape="Link no perfil e no canal"):
    img = Image.new("RGB", (1080, 1350), CREME)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1080, 120], fill=VERDE)
    d.text((540, 60), marca.upper(), font=_f(54), fill=DOURADO, anchor="mm")
    try:
        f = _foto(o["imagem"]); f.thumbnail((860, 760))
        img.paste(f, ((1080 - f.width) // 2, 150 + (760 - f.height) // 2))
    except Exception as e:
        print("Aviso: foto não baixou", e)
    if o.get("desconto"):
        d.rounded_rectangle([60, 170, 330, 270], 24, fill=LARANJA)
        d.text((195, 220), f"-{o['desconto']}%", font=_f(60), fill="white", anchor="mm")
    y = 950
    for linha in textwrap.wrap(o["titulo"], 34)[:2]:
        d.text((540, y), linha, font=_f(40, False), fill=(40, 40, 40), anchor="mm"); y += 52
    d.text((540, 1105), _brl(o["preco"]), font=_f(96), fill=VERDE, anchor="mm")
    d.text((540, 1185), o["loja"], font=_f(34, False), fill=(120, 120, 120), anchor="mm")
    d.rectangle([0, 1250, 1080, 1350], fill=DOURADO)
    d.text((540, 1300), rodape, font=_f(40), fill=VERDE, anchor="mm")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    img.save(caminho, "JPEG", quality=88)

def capa(titulo, subtitulo, marca, caminho):
    img = Image.new("RGB", (1080, 1350), VERDE)
    d = ImageDraw.Draw(img)
    d.text((540, 200), marca.upper(), font=_f(60), fill=DOURADO, anchor="mm")
    y = 560
    for linha in textwrap.wrap(titulo, 16):
        d.text((540, y), linha, font=_f(100), fill=CREME, anchor="mm"); y += 120
    d.text((540, y + 60), subtitulo, font=_f(46, False), fill=DOURADO, anchor="mm")
    d.text((540, 1250), "Arraste para o lado →", font=_f(42), fill=CREME, anchor="mm")
    img.save(caminho, "JPEG", quality=88)
