from telegram import Update
from telegram.ext import Application, CommandHandler
from flask import Flask
import threading
import os

TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context):
    await update.message.reply_text(
        "Olá! Sou o bot de ajuda. Digite /ajuda para ver a lista de comandos disponíveis."
    )


async def ajuda(update: Update, context):
    await update.message.reply_text(
        "Lista de comandos disponíveis:\n"
        "/atualizar_switch - Como atualizar o Nintendo Switch(Via PC)\n"
        "/instalar_tinfoil - Como instalar o Tinfoil Privado(Apenas para contratantes)\n"
        # "/servidor_arquivos - Como acessar servidor de arquivos no Windows\n"
        "/instalar_jogos_pc - Como instalar jogos baixados no computador\n"
        "/baixar_atualizacoes - Como baixar atualizações direto do Switch\n"
        "/configurar_emunand - Configuração ou reconfiguração de EmuNAND\n"
        "/migrar_cartao - Como migrar para um cartão de memória maior\n"
        "/configurar_tinfoil - Como configurar o Tinfoil para baixar jogos grátis"
    )


async def atualizar_switch(update: Update, context):
    await update.message.reply_text(
        "🔧 Como atualizar o Nintendo Switch para todas as versões pelo Computador:\n"
        "Link: https://youtu.be/prRx1qwnQEE"
    )


async def instalar_tinfoil(update: Update, context):
    await update.message.reply_text(
        "🎮 Como instalar Tinfoil (Para servidor privado):\n"
        "Link: https://www.youtube.com/watch?v=yMhi4M08vLg "
    )


async def servidor_arquivos(update: Update, context):
    await update.message.reply_text(
        "📁 Como acessar servidor de arquivos para atualizações, modificações e jogos direto do Windows:\n"
        "Link: https://url.gratis/CcSdAz"
    )


async def instalar_jogos_pc(update: Update, context):
    await update.message.reply_text(
        "💾 Como instalar jogos por arquivos baixados no computador:\n"
        "Link: https://abrir.link/xiWjW"
    )


async def baixar_atualizacoes(update: Update, context):
    await update.message.reply_text(
        "📡 Como baixar atualizações direto do Switch:\n"
        "Instruções: Realizar primeiro a atualização manual no primeiro item desse artigo.\n"
        "Link: https://www.youtube.com/watch?v=uGilRjPiZvM"
    )


async def configurar_emunand(update: Update, context):
    await update.message.reply_text(
        "⚙️ Configuração ou reconfiguração de EmuNAND:\n"
        "Link: https://youtu.be/cV44016kquI"
    )


async def migrar_cartao(update: Update, context):
    await update.message.reply_text(
        "💾 Como migrar para um cartão de memória maior:\n"
        "Link: https://youtu.be/bhNEleowFVc"
    )


async def configurar_tinfoil(update: Update, context):
    await update.message.reply_text(
        "🛠️ Como configurar o Tinfoil:\n"
        "1️⃣ Abra o Tinfoil e vá até 'file browse' ou 'explorador de arquivos'.\n"
        "2️⃣ Aperte '-' do Joy-Con para adicionar a loja.\n"
        "   - Protocol: http\n"
        "   - Host: 58.9.110.20\n"
        "   - Login: (deixe em branco)\n"
        "   - Senha: (deixe em branco)\n"
        "   - Port: 54331\n"
        "   - Title: Shop Thay\n"
        "3️⃣ Pressione 'X' para salvar.\n"
        "4️⃣ Feche e abra o Tinfoil novamente.\n"
        "✅ Agora você pode baixar jogos no Tinfoil de graça!"
    )


server = Flask(__name__)


@server.route("/")
def home():
    return "Bot Telegram está online!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)


def main():
    threading.Thread(target=run_web).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("atualizar_switch", atualizar_switch))
    app.add_handler(CommandHandler("instalar_tinfoil", instalar_tinfoil))
    app.add_handler(CommandHandler("servidor_arquivos", servidor_arquivos))
    app.add_handler(CommandHandler("instalar_jogos_pc", instalar_jogos_pc))
    app.add_handler(CommandHandler("baixar_atualizacoes", baixar_atualizacoes))
    app.add_handler(CommandHandler("configurar_emunand", configurar_emunand))
    app.add_handler(CommandHandler("migrar_cartao", migrar_cartao))
    app.add_handler(CommandHandler("configurar_tinfoil", configurar_tinfoil))

    print("Bot está rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()
