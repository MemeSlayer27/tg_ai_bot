from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import openai
from dotenv import load_dotenv
import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

tg_token       = os.getenv("TG_TOKEN")
openai.api_key = os.getenv("OPENAI_TOKEN")

messageList=[
            {"role": "system", "content": "You are a helpful assistant."},
        ]

tokens_used = 0

async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == "/ai":
        messageList.clear()
        messageList.append({"role": "system", "content": "You are a helpful assistant."})
        return

    messageList.append({"role": "user", "content": update.message.text})
    placeholder_message = await context.bot.send_message(chat_id=update.effective_chat.id, text="Työstän vastausta...")

    try:
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messageList
        )
        
        messageList.append(completion.choices[0].message)
        print(completion.usage.total_tokens)

        tokens_used = completion.usage.total_tokens
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=placeholder_message.message_id, text=completion.choices[0].message.content)

    except: 
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=placeholder_message.message_id, text="Jotain meni mönkään!!! Yritä myöhemmin uudestaan!")

    if tokens_used > 3200:
        messageList.clear()
        messageList.append({"role": "system", "content": "You are a helpful assistant. "})
        return


async def pong(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("pong")


app = ApplicationBuilder().token(tg_token).build()

app.add_handler(CommandHandler("ai", get_answer))

app.add_handler(CommandHandler("ping", pong))

app.run_polling()