"""Gera o Reels do dia (vídeo vertical de ~15s com os achados) a partir das artes.
python motor/reels.py gerar  -> cria docs/reels/AAAA-MM-DD.mp4 (antes do push)
A publicação é feita por social.py, depois que o vídeo está público."""
import json, os, subprocess, sys
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageDraw, ImageFont

BRT = timezone(timedelta(hours=-3))
VERDE, OURO, CREME = (31, 59, 45), (201, 164, 76), (246, 240, 228)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def _fonte(t):
    return ImageFont.truetype(FB, t)

def _centro(d, y, txt, f, cor):
    w = d.textlength(txt, font=f); d.text(((1080 - w) / 2, y), txt, font=f, fill=cor)

def _quebra(txt, f, d, larg=960):
    linhas, atual = [], ""
    for p in txt.split():
        t = (atual + " " + p).strip()
        if d.textlength(t, font=f) <= larg: atual = t
        else: linhas.append(atual); atual = p
    return linhas + ([atual] if atual else [])

def tela_card(card, n, total, saida):
    im = Image.new("RGB", (1080, 1920), VERDE); d = ImageDraw.Draw(im)
    _centro(d, 150, f"ACHADO {n} DE {total}", _fonte(58), OURO)
    c = Image.open(card).convert("RGB").resize((1000, 1250))
    im.paste(c, (40, 290))
    _centro(d, 1640, "Comenta LINK", _fonte(76), CREME)
    _centro(d, 1745, "que eu te mando no direct", _fonte(48), OURO)
    im.save(saida, quality=92)

def tela_texto(linhas, saida, destaque=None):
    im = Image.new("RGB", (1080, 1920), VERDE); d = ImageDraw.Draw(im)
    y = 620
    for txt, tam, cor in linhas:
        f = _fonte(tam)
        for l in _quebra(txt, f, d):
            _centro(d, y, l, f, cor); y += int(tam * 1.25)
        y += 40
    im.save(saida, quality=92)

def gerar(cfg, hist, data):
    hoje = [v for v in hist["vitrine"] if v.get("card") and v.get("data") == data and os.path.exists(v["card"])]
    hoje = sorted(hoje, key=lambda o: o.get("desconto", 0), reverse=True)[:cfg.get("reels_itens", 4)]
    if len(hoje) < 2:
        print("Reels: poucas ofertas hoje."); return None
    os.makedirs("docs/reels", exist_ok=True); tmp = "/tmp/reels"; os.makedirs(tmp, exist_ok=True)
    telas = []
    maior = max(o.get("desconto", 0) for o in hoje)
    tela_texto([(f"ATÉ {maior}% OFF" if maior else "ACHADOS DO DIA", 120, OURO),
                (f"{len(hoje)} achados que valem a pena hoje", 70, CREME),
                (cfg["marca"], 52, OURO)], f"{tmp}/0.jpg"); telas.append((f"{tmp}/0.jpg", 2.5))
    for i, o in enumerate(hoje, 1):
        tela_card(o["card"], i, len(hoje), f"{tmp}/{i}.jpg"); telas.append((f"{tmp}/{i}.jpg", 3.0))
    tela_texto([("QUER OS LINKS?", 110, OURO), ("Comenta LINK", 96, CREME),
                ("que eu te mando tudo no direct", 60, CREME), ("Siga para não perder os achados de amanhã", 46, OURO)],
               f"{tmp}/fim.jpg"); telas.append((f"{tmp}/fim.jpg", 3.0))
    lista = f"{tmp}/lista.txt"
    with open(lista, "w") as f:
        for p, dur in telas:
            f.write(f"file '{p}'\nduration {dur}\n")
        f.write(f"file '{telas[-1][0]}'\n")
    saida = f"docs/reels/{data}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista,
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-vf", "fps=30,format=yuv420p",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-c:a", "aac", "-shortest",
                    "-movflags", "+faststart", saida], check=True)
    for f in os.listdir("docs/reels"):
        if f < f"{(datetime.fromisoformat(data) - timedelta(days=3)).date().isoformat()}":
            os.remove(f"docs/reels/{f}")
    print("Reels gerado:", saida, len(hoje), "achados")
    return saida

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cfg = json.load(open("config.json", encoding="utf-8")); hist = json.load(open("data/historico.json"))
    agora = datetime.now(BRT); data = agora.date().isoformat()
    forcar = "--forcar" in sys.argv
    if not forcar and (agora.hour < cfg.get("reels_hora_minima", 12) or hist.get("ultimo_reels") == data or os.path.exists(f"docs/reels/{data}.mp4")):
        sys.exit(0)
    gerar(cfg, hist, data)
