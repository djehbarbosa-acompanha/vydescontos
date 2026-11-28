"""Bloqueia produtos com cara de réplica ou imitação de marca.
Regras em config.json -> "bloqueio_replicas". Mantém acessórios "para/compatível com" a marca
e produtos de lojas oficiais."""
import re, unicodedata

def _norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t)

def _tem(texto, termo):
    return re.search(r"(?<![a-z0-9])" + re.escape(_norm(termo)) + r"(?![a-z0-9])", texto) is not None

def motivo(o, regras):
    """Devolve o motivo do bloqueio, ou None se a oferta pode ser publicada."""
    titulo = _norm(o.get("titulo")); loja = _norm(o.get("shop") or o.get("loja_nome") or "")
    for termo in regras.get("termos", []):
        if _tem(titulo, termo):
            return f"termo '{termo}'"
    oficial = any(_tem(loja, p) for p in ("oficial", "official", "store oficial"))
    for marca in regras.get("marcas", []):
        m = _norm(marca)
        if not _tem(titulo, m) or oficial or _tem(loja, m):
            continue
        # acessório compatível: "capa para iphone", "pulseira compativel com apple watch"
        if re.search(r"(para|compativel com|compativel|p/)\s+(o |a )?" + re.escape(m), titulo):
            continue
        return f"marca '{marca}' fora de loja oficial"
    return None

def filtrar(ofertas, regras):
    if not regras or not regras.get("ativo", True):
        return ofertas
    ok = []
    for o in ofertas:
        m = motivo(o, regras)
        if m:
            print("Bloqueada (possível réplica):", m, "|", (o.get("titulo") or "")[:70])
        else:
            ok.append(o)
    return ok
