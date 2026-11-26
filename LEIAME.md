# Vydescontos – máquina de ofertas de afiliado (Fase 2)

## O que roda sozinho, 3 vezes por dia (8h, 12h e 19h)
1. **Escolhe as ofertas**: busca na API de Afiliados da Shopee e soma as do Mercado Livre (`data/mercadolivre.csv`). Filtra por desconto, nota, vendas e comissão, sem repetir oferta por 7 dias.
2. **Campanhas automáticas**: em Black Friday, 12.12, Natal, Volta às aulas, Dia das Mães e Dia dos Namorados, o motor troca as palavras-chave e a chamada sozinho (`campanhas` no `config.json`).
3. **Cria as artes**: uma arte 1080x1350 por oferta, com a marca, a foto, o desconto e o preço, mais a capa do dia.
4. **Publica no canal do Telegram.**
5. **Manda para o SEU Telegram** as ofertas já em texto de WhatsApp. É só copiar e colar no canal ou grupo de WhatsApp e nos stories (5 minutos por dia).
6. **Pinterest**: um pin por oferta. O Pinterest traz visitas por meses, porque as pessoas pesquisam lá.
7. **Instagram**: às 19h, um carrossel com as 5 melhores ofertas do dia.
8. **Site**: atualiza a vitrine, que é o link da bio.
9. **Rastreio**: cada canal tem o próprio link (subId). No painel de afiliados da Shopee, em Relatórios, filtrando por Sub ID, você vê de onde vem cada venda.

Cada canal liga sozinho quando os Secrets dele estão cadastrados. Sem os Secrets, o canal é só pulado.

> Senhas, tokens e App Secret NUNCA vão no chat nem nos arquivos. Só nos Secrets do GitHub.

## Secrets (Settings → Secrets and variables → Actions → New repository secret)
| Secret | O que é | Obrigatório |
| --- | --- | --- |
| `SHOPEE_APP_ID` / `SHOPEE_SECRET` | Credencial da API de Afiliados da Shopee | Sim |
| `TELEGRAM_TOKEN` | Token do robô (@BotFather) | Para Telegram e resumo |
| `TELEGRAM_CANAL` | @ do canal, ex.: `@vydescontos` | Para o canal |
| `TELEGRAM_MEU_CHAT` | Seu número de chat (mande "oi" para @userinfobot, ele responde o "Id") e depois mande /start para o seu robô | Para o resumo de WhatsApp |
| `PINTEREST_TOKEN` / `PINTEREST_BOARD` | Token da API do Pinterest e ID da pasta | Para o Pinterest |
| `IG_TOKEN` / `IG_USER_ID` | Token de longa duração da API do Instagram e ID da conta profissional | Para o Instagram |

## Passo a passo
1. **GitHub**: crie o repositório público `vydescontos` e envie todos os arquivos desta pasta, incluindo a pasta `.github`.
2. **Secrets**: cadastre pelo menos os da Shopee e do Telegram.
3. **Site**: Settings → Pages → Deploy from a branch → `main` / `/docs`. O endereço fica `https://SEU-USUARIO.github.io/vydescontos/`. Coloque esse link na bio do Instagram.
4. **Teste**: Actions → *Testar conexao Shopee* → Run workflow. Deve aparecer "Conexão OK".
5. **Primeira rodada**: Actions → *Motor de ofertas* → Run workflow.

## Pinterest (vale muito a pena para afiliado)
1. Crie uma conta comercial no Pinterest com o nome Vydescontos e uma pasta "Achados do dia".
2. Em developers.pinterest.com, crie um app e gere um token com permissão `pins:write` e `boards:read`.
3. O ID da pasta aparece na API (`GET /v5/boards`). O Claude pode ajudar nesse passo.

## Instagram (publicação automática)
Exige conta **profissional** (Criador ou Empresa) ligada a uma **Página do Facebook**.
1. Em developers.facebook.com, crie um app do tipo Empresa e adicione o produto "Instagram Graph API".
2. Gere um token com `instagram_basic`, `instagram_content_publish` e `pages_show_list` e troque por um token de longa duração (60 dias).
3. O `IG_USER_ID` é o ID da conta do Instagram ligada à página.
> O token do Instagram vence a cada 60 dias e precisa ser renovado.

## Ajustes (config.json)
`palavras_chave`, `desconto_minimo`, `nota_minima`, `vendas_minimas`, `ofertas_por_rodada`, `instagram_itens`, `instagram_chamada`, `hashtags` e `campanhas` (datas, chamada e palavras de cada campanha).
