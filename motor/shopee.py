"""Busca ofertas na API oficial de Afiliados da Shopee (Brasil)."""
import hashlib, json, os, time, urllib.request

ENDPOINT = "https://open-api.affiliate.shopee.com.br/graphql"

QUERY = """query($keyword:String,$sortType:Int,$page:Int,$limit:Int){
  productOfferV2(keyword:$keyword, sortType:$sortType, page:$page, limit:$limit){
    nodes{ itemId productName priceMin priceMax priceDiscountRate commissionRate
           imageUrl offerLink shopName sales ratingStar }
  }
}"""

def _chamar(query, variaveis):
    app_id = os.environ["SHOPEE_APP_ID"]; secret = os.environ["SHOPEE_SECRET"]
    payload = json.dumps({"query": query, "variables": variaveis}, separators=(",", ":"))
    ts = str(int(time.time()))
    assinatura = hashlib.sha256((app_id + ts + payload + secret).encode()).hexdigest()
    req = urllib.request.Request(ENDPOINT, data=payload.encode(), method="POST", headers={
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
    d = _chamar(QUERY, {"keyword": palavra, "sortType": 2, "page": 1, "limit": limite})
    ofertas = []
    for n in d["productOfferV2"]["nodes"]:
        ofertas.append({
            "loja": "Shopee",
            "id": f"shopee-{n['itemId']}",
            "titulo": n["productName"],
            "preco": float(n["priceMin"]),
            "desconto": int(n.get("priceDiscountRate") or 0),
            "comissao": float(n.get("commissionRate") or 0),
            "imagem": n["imageUrl"],
            "link": n["offerLink"],
            "vendas": int(n.get("sales") or 0),
            "nota": float(n.get("ratingStar") or 0),
        })
    return ofertas

MUT_LINK = """mutation($url:String!,$sub:[String]){
  generateShortLink(input:{originUrl:$url, subIds:$sub}){ shortLink }
}"""

def link_rastreado(url, canal):
    """Gera link curto com subId do canal (ex.: instagram), para medir de onde vêm as vendas."""
    try:
        d = _chamar(MUT_LINK, {"url": url, "sub": [canal]})
        return d["generateShortLink"]["shortLink"] or url
    except Exception as e:
        print("Aviso: link rastreado falhou", canal, e)
        return url
