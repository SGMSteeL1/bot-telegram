import os

from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


TOKEN = os.environ["BOT_TOKEN"]

TUTORIALS = {
    "atualizar_switch": {
        "title": "Como atualizar o Nintendo Switch para todas as versões pelo Computador",
        "link": "https://youtu.be/prRx1qwnQEE",
    },
    "instalar_jogos_pc": {
        "title": "Como instalar jogos por arquivos baixados no computador e usar Bot do Telegram (Torrent)",
        "link": "https://encurtador.com.br/Pszl",
    },
    "baixar_atualizacoes": {
        "title": "Como baixar atualizações direto do Switch",
        "link": "https://www.youtube.com/watch?v=uGilRjPiZvM",
    },
    "configurar_emunand": {
        "title": "Configuração ou reconfiguração de EmuNAND",
        "description": "Para quem perdeu seus dados e quer refazer o sistema.",
        "link": "https://youtu.be/cV44016kquI",
    },
    "migrar_cartao": {
        "title": "Como migrar para um cartão de memória maior",
        "link": "https://youtu.be/bhNEleowFVc",
    },
    "telegram_joguinhos": {
        "title": "Telegram de Joguinhos",
        "link": "https://nswtl.info/",
    },
    "baixar_torrent_switch": {
        "title": "Baixar Jogos via torrent direto do Switch + Bot Telegram",
        "link": "https://shre.ink/GtEz",
    },
}

USAGE_NOTICE = (
    "Use os tutoriais apenas com conteúdos, arquivos e backups que você tem direito de acessar."
)


def build_menu_text() -> str:
    lines = [
        "Olá! Sou o bot de ajuda para tutoriais de Nintendo Switch.",
        "",
        "Digite um dos comandos abaixo:",
    ]

    for command, tutorial in TUTORIALS.items():
        lines.append(f"/{command} - {tutorial['title']}")

    lines.extend(["", USAGE_NOTICE])
    return "\n".join(lines)


def build_tutorial_text(command: str) -> str:
    tutorial = TUTORIALS[command]
    lines = [tutorial["title"]]

    if tutorial.get("description"):
        lines.extend(["", tutorial["description"]])

    lines.extend(["", f"Link: {tutorial['link']}"])
    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(build_menu_text())


async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(build_menu_text())


def create_tutorial_handler(command: str):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message:
            await update.message.reply_text(build_tutorial_text(command))

    return handler


async def comando_desconhecido(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Comando não encontrado. Digite /ajuda para ver a lista de opções disponíveis."
        )


def build_telegram_app() -> Application:
    app = Application.builder().token(TOKEN).updater(None).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", ajuda))

    for command in TUTORIALS:
        app.add_handler(CommandHandler(command, create_tutorial_handler(command)))

    app.add_handler(MessageHandler(filters.COMMAND, comando_desconhecido))
    return app


async def health_check(request: web.Request) -> web.Response:
    return web.Response(text="Bot Telegram está online!")


async def telegram_webhook(request: web.Request) -> web.Response:
    telegram_app: Application = request.app["telegram_app"]
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return web.Response(text="ok")


async def on_startup(app: web.Application) -> None:
    telegram_app: Application = app["telegram_app"]
    webhook_url = app["webhook_url"]
    webhook_path = app["webhook_path"]
    drop_pending_updates = app["drop_pending_updates"]

    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.bot.set_webhook(
        url=f"{webhook_url}/{webhook_path}",
        drop_pending_updates=drop_pending_updates,
    )

    print(f"Bot está rodando via webhook em {webhook_url}/{webhook_path}")


async def on_cleanup(app: web.Application) -> None:
    telegram_app: Application = app["telegram_app"]
    await telegram_app.stop()
    await telegram_app.shutdown()


def main() -> None:
    port = int(os.environ.get("PORT", 10000))
    webhook_url = os.environ["WEBHOOK_URL"].rstrip("/")
    webhook_path = os.environ.get("WEBHOOK_PATH", "telegram-webhook").strip("/")
    drop_pending_updates = os.environ.get("DROP_PENDING_UPDATES", "false").lower() == "true"

    web_app = web.Application()
    web_app["telegram_app"] = build_telegram_app()
    web_app["webhook_url"] = webhook_url
    web_app["webhook_path"] = webhook_path
    web_app["drop_pending_updates"] = drop_pending_updates
    web_app.router.add_get("/", health_check)
    web_app.router.add_post(f"/{webhook_path}", telegram_webhook)
    web_app.on_startup.append(on_startup)
    web_app.on_cleanup.append(on_cleanup)

    web.run_app(web_app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
