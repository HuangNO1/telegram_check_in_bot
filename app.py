import os
import configparser
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
import requests
import _thread
import time

config = configparser.ConfigParser()
config.optionxform = str
config.read("token.ini")

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
    update.message.reply_text("Hello! Welcome to punched-card bot.")

def help(update: Update, context: CallbackContext):
    update.message.reply_text("""
    The following commands are available:

    /start -> Welcome Message
    /help -> This Message
    /content -> Information About Punched-card Bot
    """)


def content(update: Update, context: CallbackContext) -> None:
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


def timing(updater, delay):
    time.sleep(delay)


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(
            alarm, due, context=chat_id, name=str(chat_id))

        text = 'Timer successfully set!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)

def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(
        TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)
    # Get the dispatcher to register handlers
    disp = updater.dispatcher
    # on different commands - answer in Telegram
    disp.add_handler(CommandHandler("start", start))
    disp.add_handler(CommandHandler("help", help))
    disp.add_handler(CommandHandler("content", content))
    disp.add_handler(CommandHandler("joke", random_joke))
    disp.add_handler(MessageHandler(Filters.text, handler_message))
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
