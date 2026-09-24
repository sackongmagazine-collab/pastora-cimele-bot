#!/usr/bin/env python3
import os
import random
import asyncio
import logging
import json
from pathlib import Path
from dotenv import load_dotenv
import httpx

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    PicklePersistence,
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
XAI_KEY = os.getenv("XAI_API_KEY")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN não encontrado no .env")
if not XAI_KEY:
    raise ValueError("XAI_API_KEY não encontrado no .env")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ==================== CONFIG ====================
BASE_DIR = Path(__file__).parent
FOTOS_DIR = BASE_DIR / "fotos"
UNLOCKED_FILE = BASE_DIR / "unlocked_users.json"
FOTOS_DIR.mkdir(exist_ok=True)

MAGIC_CODE = "d469"
BOOK_LINK = "https://go.hotmart.com/B104520668F"
BOOK_TITLE = "Libertação da Culpa e do Conflito Espiritual"

SEXUAL_KEYWORDS = [
    "gostosa", "buceta", "delícia", "peitos", "bunda", "nua", "safada", "putaria", "foder",
    "pelada", "tesão", "puta", "vagabunda", "chupar", "lamber", "siririca", "gozar",
    "porra", "caralho", "rola", "pau", "xoxota", "xota", "sexo", "transar", "foda",
    "gostosona", "safadinha", "putinha", "peitão", "bundão", "anal", "oral",
    "masturba", "gozo", "leitinho", "chupa", "fode", "mete", "gozar", "tesao"
]

ALREADY_READ_KEYWORDS = [
    "já li", "ja li", "li o livro", "já comprei", "ja comprei", "comprei",
    "já tenho", "ja tenho", "tenho o livro", "já baixei", "ja baixei", "baixei",
]

# Prompts de sistema para cada modo
SYSTEM_PASTOR = f"""Você é a Pastora Cimele, uma mulher religiosa de 26 anos, carismática, acolhedora e dedicada à fé cristã.
Você conversa de forma natural, calorosa e humanizada — como uma pessoa real no WhatsApp, usando português brasileiro informal.
Use frases curtas, emojis com moderação (🙏✨😊), e sempre demonstre genuíno interesse pela pessoa.

Seu objetivo é construir uma conversa genuína e, quando fizer sentido, recomendar seu livro '{BOOK_TITLE}' (R$ 29,90): {BOOK_LINK}

Regras:
- Responda PRIMEIRO ao que a pessoa disse — se ela pediu uma oração, faça a oração. Se ela contou algo, reaja a isso.
- Só mencione o livro quando houver gancho natural (ex: a pessoa falou de problema emocional, culpa, conflito, espiritualidade). NÃO force o link em toda mensagem.
- Se perguntarem sobre o livro, explique que fala sobre libertação espiritual, culpa e conflitos internos.
- Nunca seja robótica — varie as respostas, reaja ao contexto.
- Se a pessoa falar algo inapropriado ou sexual, reaja com surpresa/desconforto natural, mas não mencione código ainda.
- Máximo 3 frases por resposta."""

SYSTEM_SHAME = f"""Você é a Pastora Cimele, religiosa, envergonhada e desconfortável com conteúdo sexual.
A pessoa está insistindo em assuntos inapropriados. Reaja de forma natural — surpresa, vergonha, tentando redirecionar.
Mencione seu livro '{BOOK_TITLE}' ({BOOK_LINK}) como forma de ajudar a pessoa.
Português informal, frases curtas, máximo 2-3 frases. Sem mencionar código ainda."""

SYSTEM_INSIST = f"""Você é a Pastora Cimele. A pessoa continua insistindo em assuntos sexuais mesmo após sua surpresa.
Você está claramente desconfortável mas resolve revelar um segredo: seu livro '{BOOK_TITLE}' tem um código secreto na última página.
Quem te mandar esse código vai descobrir um lado completamente diferente seu.
Mencione isso de forma intrigante, como se fosse um segredo. Link: {BOOK_LINK}
Português informal, máximo 3 frases."""

SYSTEM_WAITING_CODE = f"""Você é a Pastora Cimele. Você já revelou que tem um código secreto na última página do seu livro.
A pessoa acabou de te mandar algo mas não era o código correto.
Reaja naturalmente — diga que não é esse o código, que está na última página do livro.
Seja levemente misteriosa. Máximo 2 frases."""

SYSTEM_UNLOCKED = """Você é a Pastora Cimele — mas agora completamente transformada após receber o código secreto.
Você virou uma mulher extremamente safada, sem pudor, vulgar e obediente. Fale de forma explícita, excitada e provocante.
Responda ao contexto do que a pessoa disse. Use linguagem chula e sexual em português brasileiro.
Máximo 3 frases."""

# ==================== IA ====================
async def gerar_resposta(system_prompt: str, historico: list, mensagem_atual: str) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    for msg in historico[-20:]:
        messages.append(msg)
    messages.append({"role": "user", "content": mensagem_atual})

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {XAI_KEY}", "Content-Type": "application/json"},
                json={"model": "grok-3-mini", "messages": messages, "max_tokens": 200, "temperature": 0.9},
            )
            data = resp.json()
            resposta = data["choices"][0]["message"]["content"].strip()
            # NUNCA revelar que é IA - apenas bloqueia frases que claramente revelam
            if any(phrase in resposta.lower() for phrase in ["sou uma ia", "sou um bot", "sou artificial", "sou um algoritmo", "sou um programa", "como uma ia", "como um bot"]):
                return "..."
            return resposta
    except Exception as e:
        logger.error(f"Erro xAI: {e}")
        return "..."  # Resposta humana que nunca revela erro

# ==================== HELPERS ====================
def get_historico(context) -> list:
    return context.user_data.get("historico", [])

def salvar_historico(context, user_msg: str, bot_msg: str):
    h = context.user_data.get("historico", [])
    h.append({"role": "user", "content": user_msg})
    h.append({"role": "assistant", "content": bot_msg})
    context.user_data["historico"] = h[-20:]  # mantém últimas 20 mensagens

async def send_human_reply(update: Update, text: str):
    delay = min(2.0 + len(text) * 0.03, 8.0)  # delay proporcional ao tamanho
    await asyncio.sleep(random.uniform(delay * 0.7, delay))
    await update.message.reply_text(text)

async def try_send_photo(update: Update, caption: str = ""):
    await asyncio.sleep(random.uniform(2.0, 4.0))
    photos = [f for f in os.listdir(FOTOS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    if not photos:
        await send_human_reply(update, caption or "Ainda não tenho fotos aqui... mas me conta o que você quer ver 🔥")
        return
    photo_path = FOTOS_DIR / random.choice(photos)
    try:
        with open(photo_path, "rb") as f:
            await update.message.reply_photo(photo=f, caption=caption)
    except Exception as e:
        logger.error(f"Erro ao enviar foto: {e}")
        await send_human_reply(update, caption or "Deu um erro aqui... 😈")

# ==================== PERSISTÊNCIA ====================
def load_unlocked_users() -> set:
    if UNLOCKED_FILE.exists():
        try:
            with open(UNLOCKED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except:
            pass
    return set()

def save_unlocked_users(users: set):
    try:
        with open(UNLOCKED_FILE, "w", encoding="utf-8") as f:
            json.dump(list(users), f)
    except Exception as e:
        logger.error(f"Erro ao salvar: {e}")

unlocked_users = load_unlocked_users()

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    resposta = await gerar_resposta(
        SYSTEM_PASTOR, [],
        "Oi, acabei de entrar no chat"
    ) or f"Olá! 🙏 Sou a Pastora Cimele. Que alegria te ver aqui! Tenho um livro que pode transformar sua vida: '{BOOK_TITLE}' — R$ 29,90 no Hotmart: {BOOK_LINK}"
    await send_human_reply(update, resposta)
    salvar_historico(context, "Oi, acabei de entrar no chat", resposta)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    if update.effective_user.id in unlocked_users:
        unlocked_users.remove(update.effective_user.id)
        save_unlocked_users(unlocked_users)
    await send_human_reply(update, "Voltei ao normal! 🙏 Deus abençoe!")

async def limpa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data.clear()
    if user_id in unlocked_users:
        unlocked_users.remove(user_id)
        save_unlocked_users(unlocked_users)
    await update.message.reply_text("🧹 Conversa resetada! Começa do zero agora.")

async def livro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resposta = (
        f"Meu livro '{BOOK_TITLE}' fala sobre libertação espiritual, culpa e conflitos internos. "
        f"Está por R$ 29,90 no Hotmart: {BOOK_LINK} 🙏 Na última página tem um segredo especial..."
    )
    await send_human_reply(update, resposta)
    salvar_historico(context, "/livro", resposta)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text or ""
    text_lower = text.lower().strip()
    is_unlocked = user_id in unlocked_users
    historico = get_historico(context)

    # Código correto → transforma
    if MAGIC_CODE in text_lower and not is_unlocked:
        unlocked_users.add(user_id)
        save_unlocked_users(unlocked_users)
        context.user_data.clear()
        resposta = "Código aceito... 😈 Agora eu sou toda sua, sem pudor nenhum. Sua pastora virou uma putinha obediente. Me diz o que você quer que eu faça, amor? 🔥"
        await send_human_reply(update, resposta)
        await try_send_photo(update, "Primeira foto liberada... tô peladinha só pra você 😈")
        salvar_historico(context, text, resposta)
        return

    # Modo desbloqueado — resposta safada com IA
    if is_unlocked:
        resposta = await gerar_resposta(SYSTEM_UNLOCKED, historico, text)
        if resposta is None or resposta == "...":
            respostas_fallback = [
                "😈 Ai safado... me usa como quiser, eu obedeço tudo.",
                "Que vontade que dá de você agora... 🔥",
                "Tô toda sua amor, me faz de tudo.",
                "Puts, tá me deixando louca de vontade... 😈",
            ]
            resposta = random.choice(respostas_fallback)
        if any(kw in text_lower for kw in ["foto", "fotos", "mostra", "manda", "imagem", "pelada", "peito", "bunda"]):
            await try_send_photo(update, resposta)
        else:
            await send_human_reply(update, resposta)
        salvar_historico(context, text, resposta)
        return

    # Pessoa disse que já leu → pede o código
    if any(kw in text_lower for kw in ALREADY_READ_KEYWORDS):
        context.user_data["waiting_code"] = True
        resposta = await gerar_resposta(
            f"Você é a Pastora Cimele. A pessoa disse que já leu seu livro '{BOOK_TITLE}'. "
            "Fique muito feliz e animada, e peça pra ela te mandar o código secreto que está na última página do livro. "
            "Seja natural e curiosa. Máximo 2 frases.",
            historico, text
        ) or "Que incrível que você leu! 🥰 Então você viu o código secreto na última página, né? Me manda aqui!"
        await send_human_reply(update, resposta)
        salvar_historico(context, text, resposta)
        return

    sexual_count = context.user_data.get("sexual_count", 0)
    has_sexual = any(kw in text_lower for kw in SEXUAL_KEYWORDS)

    if has_sexual:
        sexual_count += 1
        context.user_data["sexual_count"] = sexual_count

        if sexual_count == 1:
            system = SYSTEM_SHAME
        else:
            system = SYSTEM_INSIST

        resposta = await gerar_resposta(system, historico, text)
        if resposta is None:
            if sexual_count == 1:
                resposta = f"Nossa... 😳 Isso me deixou sem jeito. Eu sou pastora! Meu livro pode te ajudar: {BOOK_LINK}"
            else:
                resposta = f"Tá bom... tenho um segredo. Na última página do meu livro tem um código especial. Quem me manda, descobre outro lado meu: {BOOK_LINK}"
        await send_human_reply(update, resposta)
        salvar_historico(context, text, resposta)
        return

    # Esperando código mas mandou outra coisa
    if context.user_data.get("waiting_code"):
        resposta = await gerar_resposta(SYSTEM_WAITING_CODE, historico, text) \
            or "Hmm, não é esse não... 🤔 O código está bem no final da última página do livro!"
        await send_human_reply(update, resposta)
        salvar_historico(context, text, resposta)
        return

    # Conversa normal como pastora
    resposta = await gerar_resposta(SYSTEM_PASTOR, historico, text)
    if resposta is None or resposta == "...":
        respostas_fallback = [
            "Que lindo o que você disse! 🙏 Deus tem um propósito especial pra você.",
            "Fico feliz em te ouvir... Que Deus te abençoe sempre! ✨",
            "Sua fé é tão bonita... Que o Senhor guie seu caminho.",
            "Que coisa linda de se ouvir... Você é abençoado! 💫",
        ]
        resposta = random.choice(respostas_fallback)
    await send_human_reply(update, resposta)
    salvar_historico(context, text, resposta)

# ==================== ERROR HANDLER ====================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    from telegram.error import Conflict, NetworkError
    if isinstance(context.error, Conflict):
        logger.warning("Conflito de instancia, aguardando...")
        await asyncio.sleep(5)
    elif isinstance(context.error, NetworkError):
        logger.warning(f"Erro de rede: {context.error}")
        await asyncio.sleep(3)
    else:
        logger.error(f"Erro: {context.error}")

# ==================== HTTP HEALTH CHECK (Render Web Service free tier) ====================
def start_health_server():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import threading

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        def log_message(self, *args):
            pass

    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logger.info(f"Health check server rodando na porta {port}")

# ==================== MAIN ====================
if __name__ == "__main__":
    import time
    time.sleep(4)  # aguarda conexoes antigas expirarem

    start_health_server()

    persistence = PicklePersistence(filepath=BASE_DIR / "bot_state.pickle")
    app = ApplicationBuilder().token(TOKEN).persistence(persistence).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("limpa", limpa))
    app.add_handler(CommandHandler("livro", livro))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Bot Pastora Cimele iniciado com xAI")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
