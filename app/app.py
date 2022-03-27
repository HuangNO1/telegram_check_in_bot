import os
import configparser
from telegram import *
from telegram.ext import *
import requests
import _thread
import time
from alarm import set_timer, unset, alarm
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.optionxform = str
config.read("../settings.ini")

TOKEN = config["bot"]["API_TOKEN"]
print(TOKEN)

REQUEST_KWARGS = {
    'proxy_url': 'http://127.0.0.1:7890',
}

# proxy
proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}


def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    chat_id = update.message.chat_id
    print(f"user: {user}, chat: {chat_id}")
    buttons = [[InlineKeyboardButton("start", callback_data="start")], [InlineKeyboardButton(
        "help", callback_data="help")], [InlineKeyboardButton("joke", callback_data="joke")], [InlineKeyboardButton("content", callback_data="content")]]
    update.message.reply_text("Hello! Welcome to punched-card bot.")
    update.message.reply_text("""
    The following commands are available:

    /start -> Welcome Message
    /help -> This Message
    /content -> Information About Punched-card Bot
    """, reply_markup=InlineKeyboardMarkup(buttons))
    


def content(update: Update, context: CallbackContext) -> None:
    print(update.message.chat_id)
    update.message.reply_text("fuxk you")


def random_joke(update: Update, context: CallbackContext) -> None:
    firstname = None
    lastname = None
    try:
        firstname = context.args[0]
    except:
        print("joke no key")
    url = 'http://api.icndb.com/jokes/random?espcapt=javascript'
    if firstname:
        url += "&firstname=" + firstname
    if lastname:
        url += "&lastname=" + lastname
    resp = requests.get(url)
    resp.encoding = "utf-8"
    data = resp.json()

    update.message.reply_text(f"Fuxk you! {data['value']['joke']}")


def handler_message(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f"You said {update.message.text}")


def handler_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query.data
    if "start" in query:
        start(update.callback_query, context)
    elif "help" in query:
        start(update.callback_query, context)
    elif "joke" in query:
        random_joke(update.callback_query, context)
    elif "content" in query:
        content(update.callback_query, context)


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(
        TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)
    # Get the dispatcher to register handlers
    disp = updater.dispatcher
    # on different commands - answer in Telegram
    disp.add_handler(CommandHandler("start", start))
    disp.add_handler(MessageHandler("", start))
    disp.add_handler(CommandHandler("help", start))
    disp.add_handler(CommandHandler("content", content))
    disp.add_handler(CommandHandler("joke", random_joke))
    disp.add_handler(CommandHandler("set", set_timer))
    disp.add_handler(CommandHandler("unset", unset))
    disp.add_handler(MessageHandler(Filters.text, handler_message))
    disp.add_handler(CallbackQueryHandler(handler_query))

    # disp.job_queue.run_repeating(
    #     alarm, 5, context=-1001306240493, name=str(-1001306240493))
    # try:
    #    _thread.start_new_thread(timing, (updater, 5,))
    # except:
    #    print("Error: unable to start thread")
    # Start the Bot
    updater.start_polling()
    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
