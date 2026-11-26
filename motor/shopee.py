"""Busca ofertas na API oficial de Afiliados da Shopee (Brasil)."""
import hashlib, json, os, time, urllib.request

ENDPOINT = "https://open-api.affiliate.shopee.com.br/graphql"
CAMPOS = "itemId productName priceMin priceMax priceDiscountRate commissionRate imageUrl offerLink shopName sales ratingStar"

def _chamar(query):
    app_id = os.environ["SHOPEE_APP_ID"].strip(); secret = os.environ["SHOPEE_SECRET"].strip()
    payload = json.dumps({"query": query}, separators=(",", ":"), ensure_ascii=False)
    ts = str(int(time.time()))
    assinatura = hashlib.sha256((app_id + ts + payload + secret).encode("utf-8")).hexdigest()
    req = urllib.request.Request(ENDPOINT, data=payload.encode("utf-8"), method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": f"SHA256 Credential={app_id}, Timestamp={ts}, Signature={assinatura}",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        dados = json.load(r)
    if dados.get("errors"):
        raise RuntimeError(dados["errors"])
    return dados["data"]

def buscar(palavra, limite=30):
    """sortType 2 = mais vendidos."""
    q = "{productOfferV2(keyword:%s,sortType:2,page:1,limit:%d){nodes{%s}}}" % (json.dumps(palavra, ensure_ascii=False), limite, CAMPOS)
    d = _chamar(q)
    ofertas = []
    for n in d["productOfferV2"]["nodes"]:
        ofertas.append({
            "loja": "Shopee",
            "id": f"shopee-{n['itemId']}",
            "titulo": n["productName"],
            "preco": float(n["priceMin"]),
            "desconto": int(float(n.get("priceDiscountRate") or 0)),
            "comissao": float(n.get("commissionRate") or 0),
            "imagem": n["imageUrl"],
            "link": n["offerLink"],
            "vendas": int(n.get("sales") or 0),
            "nota": float(n.get("ratingStar") or 0),
        })
    return ofertas

def link_rastreado(url, canal):
    """Gera link curto com subId do canal (ex.: instagram), para medir de onde vêm as vendas."""
    try:
        q = 'mutation{generateShortLink(input:{originUrl:%s,subIds:[%s]}){shortLink}}' % (json.dumps(url), json.dumps(canal))
        return _chamar(q)["generateShortLink"]["shortLink"] or url
    except Exception as e:
        print("Aviso: link rastreado falhou", canal, e)
        return url
