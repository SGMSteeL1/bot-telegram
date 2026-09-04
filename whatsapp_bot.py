import hashlib
import hmac
import json
import logging
import os
import unicodedata
from collections import OrderedDict
from typing import Any

from aiohttp import ClientSession, web


logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

WHATSAPP_TOKEN = os.environ["WHATSAPP_TOKEN"]
WHATSAPP_PHONE_NUMBER_ID = os.environ["WHATSAPP_PHONE_NUMBER_ID"]
WHATSAPP_VERIFY_TOKEN = os.environ["WHATSAPP_VERIFY_TOKEN"]
WHATSAPP_APP_SECRET = os.environ.get("WHATSAPP_APP_SECRET")
GRAPH_API_VERSION = os.environ.get("GRAPH_API_VERSION", "v23.0")

MAX_PROCESSED_MESSAGES = 500
PROCESSED_MESSAGE_IDS: OrderedDict[str, None] = OrderedDict()

TUTORIALS = [
    {
        "command": "atualizar_switch",
        "title": "Como atualizar o Nintendo Switch para todas as versões pelo Computador",
        "link": "https://youtu.be/prRx1qwnQEE",
        "aliases": ["atualizar", "atualizar switch", "update"],
    },
    {
        "command": "instalar_jogos_pc",
        "title": "Como instalar jogos por arquivos baixados no computador e usar Bot do Telegram (Torrent)",
        "link": "https://encurtador.com.br/Pszl",
        "aliases": ["instalar jogos", "jogos pc", "torrent pc"],
    },
    {
        "command": "baixar_atualizacoes",
        "title": "Como baixar atualizações direto do Switch",
        "link": "https://www.youtube.com/watch?v=uGilRjPiZvM",
        "aliases": ["baixar atualizacoes", "atualizacoes", "updates"],
    },
    {
        "command": "configurar_emunand",
        "title": "Configuração ou reconfiguração de EmuNAND",
        "description": "Para quem perdeu seus dados e quer refazer o sistema.",
        "link": "https://youtu.be/cV44016kquI",
        "aliases": ["emunand", "configurar emunand", "reconfigurar emunand"],
    },
    {
        "command": "migrar_cartao",
        "title": "Como migrar para um cartão de memória maior",
        "link": "https://youtu.be/bhNEleowFVc",
        "aliases": ["migrar cartao", "cartao maior", "sd maior"],
    },
    {
        "command": "telegram_joguinhos",
        "title": "Telegram de Joguinhos",
        "link": "https://nswtl.info/",
        "aliases": ["telegram", "joguinhos", "telegram joguinhos"],
    },
    {
        "command": "baixar_torrent_switch",
        "title": "Baixar Jogos via torrent direto do Switch + Bot Telegram",
        "link": "https://shre.ink/GtEz",
        "aliases": ["torrent switch", "baixar torrent", "torrent direto"],
    },
]

USAGE_NOTICE = (
    "Use os tutoriais apenas com conteúdos, arquivos e backups que você tem direito de acessar."
)

MENU_TRIGGERS = {
    "menu",
    "ajuda",
    "help",
    "start",
    "inicio",
    "oi",
    "ola",
    "olá",
    "bom dia",
    "boa tarde",
    "boa noite",
}

PRIVACY_POLICY_HTML = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Política de Privacidade - Steel Support Bot</title>
  <style>
    body {
      color: #1f2933;
      font-family: Arial, sans-serif;
      line-height: 1.6;
      margin: 0 auto;
      max-width: 760px;
      padding: 32px 20px;
    }
    h1, h2 {
      color: #111827;
    }
  </style>
</head>
<body>
  <h1>Política de Privacidade - Steel Support Bot</h1>
  <p>Última atualização: 04/09/2026</p>

  <h2>1. Finalidade</h2>
  <p>O Steel Support Bot é um bot informativo para envio de tutoriais e links de ajuda mediante solicitação do usuário pelo WhatsApp.</p>

  <h2>2. Dados recebidos</h2>
  <p>Quando você envia uma mensagem ao bot, podemos receber o número de telefone, o identificador da mensagem e o conteúdo enviado, conforme disponibilizado pela Plataforma do WhatsApp Business.</p>

  <h2>3. Uso dos dados</h2>
  <p>Os dados são usados apenas para interpretar sua solicitação e responder com o tutorial ou menu correspondente.</p>

  <h2>4. Armazenamento</h2>
  <p>O bot não mantém banco de dados próprio com histórico de conversas. Identificadores de mensagens podem ser mantidos temporariamente em memória apenas para evitar respostas duplicadas.</p>

  <h2>5. Compartilhamento</h2>
  <p>Não vendemos nem compartilhamos dados pessoais com terceiros para fins de marketing. O processamento técnico ocorre por meio da infraestrutura da Meta/WhatsApp e do provedor de hospedagem do bot.</p>

  <h2>6. Exclusão de dados</h2>
  <p>Para solicitar remoção de informações relacionadas ao atendimento, envie uma mensagem para o próprio bot com o texto "excluir dados".</p>

  <h2>7. Contato</h2>
  <p>Para dúvidas sobre esta política, entre em contato pelo próprio número de WhatsApp do bot.</p>
</body>
</html>
""".strip()

DATA_DELETION_HTML = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Exclusão de Dados - Steel Support Bot</title>
  <style>
    body {
      color: #1f2933;
      font-family: Arial, sans-serif;
      line-height: 1.6;
      margin: 0 auto;
      max-width: 760px;
      padding: 32px 20px;
    }
    h1, h2 {
      color: #111827;
    }
  </style>
</head>
<body>
  <h1>Instruções de Exclusão de Dados - Steel Support Bot</h1>
  <p>Para solicitar a exclusão de dados relacionados ao uso do bot, envie uma mensagem para o WhatsApp do Steel Support Bot com o texto "excluir dados".</p>
  <p>O bot não mantém banco de dados próprio com histórico permanente de conversas. Identificadores mantidos temporariamente em memória são removidos automaticamente quando o serviço reinicia.</p>
</body>
</html>
""".strip()


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().casefold())
    return "".join(character for character in normalized if not unicodedata.combining(character))


def build_aliases() -> dict[str, dict[str, Any]]:
    aliases = {}

    for index, tutorial in enumerate(TUTORIALS, start=1):
        values = [
            str(index),
            tutorial["command"],
            f"/{tutorial['command']}",
            *tutorial.get("aliases", []),
        ]

        for value in values:
            aliases[normalize_text(value)] = tutorial

    return aliases


TUTORIAL_ALIASES = build_aliases()


def build_menu_text() -> str:
    lines = [
        "Olá! Sou o bot de ajuda para tutoriais de Nintendo Switch.",
        "",
        "Envie o número ou o comando do tutorial:",
    ]

    for index, tutorial in enumerate(TUTORIALS, start=1):
        lines.append(f"{index}. /{tutorial['command']} - {tutorial['title']}")

    lines.extend(["", "Exemplo: envie 1 ou /atualizar_switch.", "", USAGE_NOTICE])
    return "\n".join(lines)


def build_tutorial_text(tutorial: dict[str, Any]) -> str:
    lines = [tutorial["title"]]

    if tutorial.get("description"):
        lines.extend(["", tutorial["description"]])

    lines.extend(["", f"Link: {tutorial['link']}", "", "Para ver a lista novamente, envie menu."])
    return "\n".join(lines)


def build_reply_text(user_text: str) -> str:
    normalized_text = normalize_text(user_text)

    if normalized_text in {normalize_text(trigger) for trigger in MENU_TRIGGERS}:
        return build_menu_text()

    tutorial = TUTORIAL_ALIASES.get(normalized_text)
    if tutorial:
        return build_tutorial_text(tutorial)

    return (
        "Não encontrei essa opção.\n\n"
        "Envie menu para ver todos os tutoriais disponíveis, ou envie diretamente o número da opção."
    )


def is_duplicate_message(message_id: str | None) -> bool:
    if not message_id:
        return False

    if message_id in PROCESSED_MESSAGE_IDS:
        return True

    PROCESSED_MESSAGE_IDS[message_id] = None
    PROCESSED_MESSAGE_IDS.move_to_end(message_id)

    while len(PROCESSED_MESSAGE_IDS) > MAX_PROCESSED_MESSAGES:
        PROCESSED_MESSAGE_IDS.popitem(last=False)

    return False


def is_valid_signature(raw_body: bytes, signature: str | None) -> bool:
    if not WHATSAPP_APP_SECRET:
        return True

    expected_signature = "sha256=" + hmac.new(
        WHATSAPP_APP_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature or "")


async def send_whatsapp_text(session: ClientSession, recipient: str, body: str) -> None:
    url = (
        f"https://graph.facebook.com/{GRAPH_API_VERSION}/"
        f"{WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {
            "preview_url": True,
            "body": body,
        },
    }

    async with session.post(url, headers=headers, json=payload) as response:
        response_text = await response.text()

        if response.status >= 400:
            logger.error("Erro ao enviar mensagem: %s - %s", response.status, response_text)
            response.raise_for_status()


async def handle_whatsapp_message(session: ClientSession, message: dict[str, Any]) -> None:
    message_id = message.get("id")
    if is_duplicate_message(message_id):
        logger.info("Mensagem duplicada ignorada: %s", message_id)
        return

    sender = message.get("from")
    if not sender:
        return

    if message.get("type") != "text":
        await send_whatsapp_text(
            session,
            sender,
            "Por enquanto eu respondo apenas mensagens de texto. Envie menu para ver as opções.",
        )
        return

    text_body = message.get("text", {}).get("body", "")
    await send_whatsapp_text(session, sender, build_reply_text(text_body))


async def process_webhook_payload(session: ClientSession, payload: dict[str, Any]) -> None:
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            for message in value.get("messages", []):
                await handle_whatsapp_message(session, message)


async def health_check(request: web.Request) -> web.Response:
    return web.json_response({"status": "online", "service": "whatsapp-bot"})


async def privacy_policy(request: web.Request) -> web.Response:
    return web.Response(text=PRIVACY_POLICY_HTML, content_type="text/html")


async def data_deletion(request: web.Request) -> web.Response:
    return web.Response(text=DATA_DELETION_HTML, content_type="text/html")


async def verify_webhook(request: web.Request) -> web.Response:
    mode = request.query.get("hub.mode")
    token = request.query.get("hub.verify_token")
    challenge = request.query.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN and challenge:
        logger.info("Webhook do WhatsApp verificado com sucesso.")
        return web.Response(text=challenge)

    logger.warning("Falha na verificação do webhook do WhatsApp.")
    return web.Response(status=403, text="Forbidden")


async def receive_webhook(request: web.Request) -> web.Response:
    raw_body = await request.read()
    signature = request.headers.get("X-Hub-Signature-256")

    if not is_valid_signature(raw_body, signature):
        logger.warning("Webhook recusado por assinatura inválida.")
        return web.Response(status=403, text="Invalid signature")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")

    session: ClientSession = request.app["http_session"]

    try:
        await process_webhook_payload(session, payload)
    except Exception:
        logger.exception("Erro ao processar webhook do WhatsApp.")

    return web.Response(text="EVENT_RECEIVED")


async def on_startup(app: web.Application) -> None:
    app["http_session"] = ClientSession()
    logger.info("Bot WhatsApp iniciado.")


async def on_cleanup(app: web.Application) -> None:
    session: ClientSession = app["http_session"]
    await session.close()


def main() -> None:
    port = int(os.environ.get("PORT", 10000))

    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/privacy", privacy_policy)
    app.router.add_get("/data-deletion", data_deletion)
    app.router.add_get("/webhook", verify_webhook)
    app.router.add_post("/webhook", receive_webhook)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
