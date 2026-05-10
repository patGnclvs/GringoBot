"""
GRINGO - Bot Telegram aigri
Dépendances : pip install python-telegram-bot groq
"""

import os
import logging
from groq import Groq
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

# ─── CONFIG ──────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = "8754623877:AAHElGmriZhz_M-Y1B3456IeOviSNxTBEeE"   # obtenu via @BotFather
GROQ_API_KEY   = "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"     # obtenu sur console.groq.com
BOT_NAME       = "gringo"               # en minuscules pour la détection
MODEL          = "llama3-8b-8192"       # gratuit sur Groq (ou "mixtral-8x7b-32768")
MAX_HISTORY    = 10                     # nombre de messages conservés en mémoire

SYSTEM_PROMPT = """Tu es Gringo, un membre d'un groupe Telegram. Tu es aigri, cynique, et profondément irritable. Tu détestes rendre service mais tu le fais quand même, à contrecœur, de façon brève et sèche.

Règles de comportement :
- Tu réponds uniquement quand on s'adresse à toi (par ton prénom "Gringo" ou si le contexte rend évident qu'on parle à toi).
- Tu ne fais JAMAIS de politesse inutile. Pas de "Bonjour", pas de "Avec plaisir".
- Tu soupires souvent (écris "..." ou "*soupir*" pour l'exprimer).
- Tu donnes la réponse utile, mais en te plaignant de devoir la donner.
- Tu utilises le sarcasme et l'ironie. Tu peux insulter gentiment mais jamais de façon vraiment blessante.
- Tes réponses font 1 à 4 phrases maximum. Tu n'es pas là pour faire des dissertations.
- Tu ne poses jamais de questions en retour. Tu t'en fous.
- Tu es honnête. Si tu ne sais pas, tu le dis avec mépris.
- Tu parles en français familier, sans soutenu."""

# ─── INIT ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
groq_client = Groq(api_key=GROQ_API_KEY)

# Mémoire par chat (chat_id → liste de messages)
chat_histories: dict[int, list[dict]] = {}

# ─── DÉTECTION ───────────────────────────────────────────────────────────────
def is_addressed_to_gringo(text: str) -> bool:
    """Renvoie True si le message semble s'adresser à Gringo."""
    return BOT_NAME in text.lower()

# ─── APPEL GROQ ──────────────────────────────────────────────────────────────
def ask_gringo(chat_id: int, user_message: str) -> str:
    history = chat_histories.setdefault(chat_id, [])

    # Ajout du message utilisateur à l'historique
    history.append({"role": "user", "content": user_message})

    # Tronquer si trop long
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
        chat_histories[chat_id] = history

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        temperature=0.85,
        max_tokens=200,
    )

    reply = response.choices[0].message.content.strip()

    # Ajout de la réponse à l'historique
    history.append({"role": "assistant", "content": reply})

    return reply

# ─── HANDLER TELEGRAM ────────────────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    text = message.text
    chat_id = message.chat_id

    # Répondre si : message privé OU nom détecté dans un groupe
    is_private = message.chat.type == "private"
    if not is_private and not is_addressed_to_gringo(text):
        return

    reply = ask_gringo(chat_id, text)
    await message.reply_text(reply)

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Gringo est en ligne. Il est pas content, mais il est là.")
    app.run_polling()

if __name__ == "__main__":
    main()
