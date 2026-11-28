"""Motor de ofertas: busca, escolhe, gera artes, publica no Telegram, manda o resumo para você e atualiza o site.
Instagram e Pinterest são publicados depois, por social.py, quando as artes já estão públicas."""
import json, os, random, sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(__file__))
import shopee, mercadolivre, telegram, vitrine, cards, filtro

BRT = timezone(timedelta(hours=-3))
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)
cfg = json.load(open("config.json", encoding="utf-8"))
HIST = "data/historico.json"
hist = json.load(open(HIST)) if os.path.exists(HIST) else {"publicadas": {}, "vitrine": []}
agora = datetime.now(timezone.utc); hoje = datetime.now(BRT).date()
limite = agora - timedelta(days=cfg["dias_sem_repetir"])
recentes = {k for k, v in hist["publicadas"].items() if datetime.fromisoformat(v) > limite}
os.makedirs("docs/cards", exist_ok=True)
tem_shopee = bool(os.environ.get("SHOPEE_APP_ID"))

# 0. Campanha do período (Black Friday, Natal, 12.12...): reforça as palavras e a chamada
campanha = next((c for c in cfg.get("campanhas", []) if c["inicio"] <= hoje.isoformat() <= c["fim"]), None)
palavras = random.sample(cfg["palavras_chave"], min(4, len(cfg["palavras_chave"])))
if campanha:
    palavras = random.sample(campanha["palavras"], min(2, len(campanha["palavras"]))) + palavras[:2]
    print("Campanha ativa:", campanha["nome"])

# 1. Coleta
candidatas = []
for p in palavras if tem_shopee else []:
    try:
        candidatas += shopee.buscar(p)
    except Exception as e:
        print("Erro Shopee", p, e)
candidatas += mercadolivre.carregar()

# 2. Filtro e pontuação (desconto, comissão e popularidade)
boas = [o for o in candidatas if o["id"] not in recentes and (
    o["loja"] != "Shopee" or (o["desconto"] >= cfg["desconto_minimo"] and o["nota"] >= cfg["nota_minima"] and o["vendas"] >= cfg["vendas_minimas"]))]
boas = filtro.filtrar(boas, cfg.get("bloqueio_replicas"))
vistas = set(); unicas = []
for o in boas:
    if o["id"] not in vistas:
        vistas.add(o["id"]); unicas.append(o)
unicas.sort(key=lambda o: (o["desconto"] * 2 + o["comissao"] * 100 + min(o["vendas"], 5000) / 500), reverse=True)
escolhidas = unicas[: cfg["ofertas_por_rodada"]]

# 3. Links rastreados por canal (subId) e artes
canais = ["telegram", "whatsapp", "instagram", "pinterest", "site"]
for o in escolhidas:
    o["links"] = {c: (shopee.link_rastreado(o["link"], c) if o["loja"] == "Shopee" and tem_shopee else o["link"]) for c in canais}
    o["data"] = hoje.isoformat()
    o["card"] = f"docs/cards/{o['id']}.jpg"
    try:
        cards.card(o, cfg["marca"], o["card"])
    except Exception as e:
        print("Erro arte", e); o["card"] = None
chamada = campanha["chamada"] if campanha else cfg["instagram_chamada"]
cards.capa(chamada, hoje.strftime("%d/%m"), cfg["marca"], "docs/cards/capa.jpg")

# 4. Telegram (canal) e resumo para você
for o in escolhidas:
    try:
        if os.environ.get("TELEGRAM_TOKEN") and os.environ.get("TELEGRAM_CANAL"):
            telegram.publicar(o, cfg["aviso_afiliado"])
        hist["publicadas"][o["id"]] = agora.isoformat()
        print("Selecionada:", o["loja"], o["titulo"][:60])
    except Exception as e:
        print("Erro Telegram", e)
try:
    telegram.resumo_para_mim(escolhidas, campanha["nome"] if campanha else None)
except Exception as e:
    print("Erro resumo", e)

# 5. Vitrine, histórico, rodada e limpeza de artes antigas
for o in escolhidas:
    o["link_vitrine"] = o["links"]["site"]
hist["vitrine"] = (escolhidas + [v for v in hist["vitrine"] if v["id"] not in {e["id"] for e in escolhidas}])[:60]
hist["publicadas"] = {k: v for k, v in hist["publicadas"].items() if datetime.fromisoformat(v) > agora - timedelta(days=30)}
json.dump(hist, open(HIST, "w"), ensure_ascii=False, indent=1)
json.dump({"ofertas": [o for o in escolhidas if o.get("card")]}, open("data/rodada.json", "w"), ensure_ascii=False, indent=1)
manter = {v.get("card") for v in hist["vitrine"]} | {"docs/cards/capa.jpg"}
for f in os.listdir("docs/cards"):
    if f"docs/cards/{f}" not in manter:
        os.remove(f"docs/cards/{f}")
vitrine.gerar(hist["vitrine"], cfg)
print(f"{len(escolhidas)} ofertas na rodada; vitrine com {len(hist['vitrine'])} itens.")
