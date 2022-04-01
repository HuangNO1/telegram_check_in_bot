import os
import configparser
from telegram import *
from telegram.ext import *
import requests
import _thread
import time
from alarm import *
from service import *
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

buttons = [[InlineKeyboardButton(
    "help", callback_data="help"), InlineKeyboardButton("joke", callback_data="joke")],
    [InlineKeyboardButton("本群打卡資訊", callback_data="get_chat_info"),
     InlineKeyboardButton("所有使用者資訊", callback_data="get_all_users_info")]]


def start(update: Update, context: CallbackContext) -> None:
    """
    start 信息
    """
    user = update.message.from_user.username
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    print(f"username: {user}, user_id: {user_id},  chat: {chat_id}")
    # update.message.reply_text("Hello! Welcome to punched-card bot.")
    update.message.reply_text("""
    The following commands are available:

/start -> Welcome Message
/help -> This Message
/content -> Information About Punched-card Bot
/get_chat_info -> 獲取本群打卡資訊
/add_chat_info -> 將本群加入打卡列表
/update_chat_alarm_times 12:00:00 13:00:00:00 -> 設定打卡提醒時段
/update_chat_alarm_days 0 1 2 3 -> 設定每週打卡日 0(週一) - 6(週日)
/update_sum_up_time 04:00:00 -> 設定每日總結昨日打卡時間
/update_chat_enable 0 -> 0 或 1 設定該群是否啟用打卡
/delete_chat_info -> 刪除群打卡與開群所有打卡紀錄
/get_user_info -> 獲取使用者打卡資訊
/get_all_users_info -> 獲取本群所有使用者資訊
/add_user_to_check_in_list -> 將自己添加進打卡列表
/user_check_in -> 使用者打卡
/delete_user_info -> 刪除使用者打卡
    """, reply_markup=InlineKeyboardMarkup(buttons))


# chat
def get_chat_info(update: Update, context: CallbackContext) -> None:
    """
    獲取本群打卡情況
    """
    chat_id = update.message.chat_id
    update.message.reply_text(get_chat_status(
        chat_id), reply_markup=InlineKeyboardMarkup(buttons))


def add_chat_info(update: Update, context: CallbackContext) -> None:
    """
    添加群打卡管理
    """
    chat_id = update.message.chat_id
    update.message.reply_text(add_chat(
        chat_id), reply_markup=InlineKeyboardMarkup(buttons))


def delete_chat_info(update: Update, context: CallbackContext) -> None:
    """
    刪除打卡管理
    """
    chat_id = update.message.chat_id
    update.message.reply_text(delete_chat(
        chat_id), reply_markup=InlineKeyboardMarkup(buttons))


def update_chat_alarm_times(update: Update, context: CallbackContext) -> None:
    """
    變更群每日打卡時間段
    """
    chat_id = update.message.chat_id

    if len(context.args) <= 0:
        update.message.reply_text(
            "沒有參數", reply_markup=InlineKeyboardMarkup(buttons))
        return

    print(context.args)
    alarm_times = context.args

    update.message.reply_text(change_chat_alarm_time(
        chat_id, alarm_times), reply_markup=InlineKeyboardMarkup(buttons))


def update_chat_alarm_days(update: Update, context: CallbackContext) -> None:
    """
    變更群每週打卡日
    """
    chat_id = update.message.chat_id

    if len(context.args) <= 0:
        update.message.reply_text(
            "沒有參數", reply_markup=InlineKeyboardMarkup(buttons))
        return

    print(context.args)
    alarm_days = tuple(context.args)
    print(alarm_days)

    update.message.reply_text(change_chat_alarm_days(
        chat_id, alarm_days), reply_markup=InlineKeyboardMarkup(buttons))


def update_sum_up_time(update: Update, context: CallbackContext) -> None:
    """
    變更每日總結昨日打卡時間
    """
    chat_id = update.message.chat_id

    if len(context.args) <= 0:
        update.message.reply_text(
            "沒有參數", reply_markup=InlineKeyboardMarkup(buttons))
        return
    sum_up_time = context.args[0]
    update.message.reply_text(change_chat_sum_up_time(
        chat_id, sum_up_time), reply_markup=InlineKeyboardMarkup(buttons))


def update_chat_enable(update: Update, context: CallbackContext) -> None:
    """
    變更是否啟用群打卡設置
    """
    chat_id = update.message.chat_id
    if len(context.args) <= 0:
        update.message.reply_text(
            "沒有參數", reply_markup=InlineKeyboardMarkup(buttons))
        return
    print(context.args)
    if str(context.args[0]) != "0" and str(context.args[0]) != "1":
        update.message.reply_text(
            "無效參數", reply_markup=InlineKeyboardMarkup(buttons))
        return
    is_alarm = True if context.args[0] == "1" else False
    update.message.reply_text(change_chat_alarm_enable(
        chat_id, is_alarm), reply_markup=InlineKeyboardMarkup(buttons))


# user
def get_all_users_info(update: Update, context: CallbackContext) -> None:
    """
    獲取所有 user 打卡信息
    """
    chat_id = update.message.chat_id
    update.message.reply_text(get_all_users_status(
        chat_id), reply_markup=InlineKeyboardMarkup(buttons))


def get_user_info(update: Update, context: CallbackContext) -> None:
    """
    獲取 user 打卡信息
    """
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    print(f"username: {username}, user_id: {user_id},  chat: {chat_id}")
    update.message.reply_text(get_user_status(
        chat_id, user_id), reply_markup=InlineKeyboardMarkup(buttons))


def add_user_to_check_in_list(update: Update, context: CallbackContext) -> None:
    """
    將 user 添加進打卡
    """
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    chat_id = update.message.chat_id

    update.message.reply_text(add_user(
        chat_id, user_id, username), reply_markup=InlineKeyboardMarkup(buttons))


def user_check_in(update: Update, context: CallbackContext) -> None:
    """
    打卡
    """
    user_id = update.message.from_user.id
    # username = update.message.from_user.username
    chat_id = update.message.chat_id
    update.message.reply_text(
        check_in(chat_id, user_id), reply_markup=InlineKeyboardMarkup(buttons))


def sum_up_chat_yesterday(update: Update, context: CallbackContext) -> None:
    """
    總結昨日打卡情況
    """
    chat_id = update.message.chat_id
    update.message.reply_text(
        sum_up_yesterday(chat_id), reply_markup=InlineKeyboardMarkup(buttons))


def delete_user_info(update: Update, context: CallbackContext) -> None:
    """
    將使用者移除打卡清單
    """
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    update.message.reply_text(
        delete_user(chat_id, user_id, username), reply_markup=InlineKeyboardMarkup(buttons))


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
    elif "get_chat_info" in query:
        get_chat_info(update.callback_query, context)
    elif "get_all_users_info" in query:
        get_all_users_info(update.callback_query, context)
    elif "get_user_info" in query:
        get_user_info(update.callback_query, context)
    elif "add_user_to_check_in_list" in query:
        add_user_to_check_in_list(update.callback_query, context)


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(
        TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)
    # Get the dispatcher to register handlers
    disp = updater.dispatcher
    print(type(disp))
    # on different commands - answer in Telegram
    disp.add_handler(CommandHandler("start", start))
    disp.add_handler(MessageHandler("", start))
    disp.add_handler(CommandHandler("help", start))
    disp.add_handler(CommandHandler("content", content))
    disp.add_handler(CommandHandler("joke", random_joke))
    disp.add_handler(CommandHandler("set", set_timer))
    disp.add_handler(CommandHandler("unset", unset))

    # chat
    disp.add_handler(CommandHandler("get_chat_info", get_chat_info))
    disp.add_handler(CommandHandler("add_chat_info", add_chat_info))
    disp.add_handler(CommandHandler(
        "update_chat_alarm_times", update_chat_alarm_times))
    disp.add_handler(CommandHandler(
        "update_chat_alarm_days", update_chat_alarm_days))
    disp.add_handler(CommandHandler(
        "update_sum_up_time", update_sum_up_time))
    disp.add_handler(CommandHandler(
        "update_chat_enable", update_chat_enable))
    disp.add_handler(CommandHandler(
        "delete_chat_info", delete_chat_info))

    # user
    disp.add_handler(CommandHandler("get_all_users_info", get_all_users_info))
    disp.add_handler(CommandHandler("get_user_info", get_user_info))
    disp.add_handler(CommandHandler(
        "add_user_to_check_in_list", add_user_to_check_in_list))
    disp.add_handler(CommandHandler(
        "user_check_in", user_check_in))
    disp.add_handler(CommandHandler(
        "delete_user_info", delete_user_info))
    disp.add_handler(CommandHandler(
        "sum_up_chat_yesterday", sum_up_chat_yesterday))

    disp.add_handler(MessageHandler(Filters.text, handler_message))
    disp.add_handler(CallbackQueryHandler(handler_query))

    start_all_chat_jobs(disp)
    # test_alarm(disp)
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
