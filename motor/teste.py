"""Teste rápido: confere se a credencial da Shopee funciona, sem publicar nada."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import shopee

if not os.environ.get("SHOPEE_APP_ID") or not os.environ.get("SHOPEE_SECRET"):
    sys.exit("Faltam os Secrets SHOPEE_APP_ID e/ou SHOPEE_SECRET no GitHub.")
try:
    ofertas = shopee.buscar("garrafa térmica", limite=5)
except Exception as e:
    sys.exit(f"A Shopee recusou a conexão: {e}\nConfira se o App ID e o App Secret foram copiados sem espaços.")
print(f"Conexão OK: {len(ofertas)} ofertas recebidas.")
for o in ofertas:
    print(f"- {o['titulo'][:70]} | R$ {o['preco']:.2f} | {o['desconto']}% OFF | comissão {o['comissao']*100:.1f}%")
if os.environ.get("TELEGRAM_TOKEN"):
    print("Telegram configurado.")
else:
    print("Telegram ainda não configurado (o motor só vai atualizar o site).")
