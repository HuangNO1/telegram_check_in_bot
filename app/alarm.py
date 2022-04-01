from dao import *
from telegram import *
from telegram.ext import *
from datetime import *
from service import *
import pytz


def start_all_chat_jobs(disp: Dispatcher) -> None:
    """
    將所有需要 job 的任務運行起來
    """
    chats = get_all_chat()

    for chat in chats:
        # 清空所有提醒
        for t in chat.alarm_times:
            job_removed = remove_job_if_exists(
                str(chat.chat_id) + " alarm" + str(t), disp)
            # 運行所有時間段 提示打卡
            disp.job_queue.run_daily(
                alarm_check_in, t, chat.alarm_days, context=chat.chat_id, name=str(chat.chat_id) + " alarm " + str(t))
        # 運行總結昨日打卡
        disp.job_queue.run_daily(alarm_sum_up_yesterday, chat.sum_up_time, chat.alarm_days,
                                 context=chat.chat_id, name=str(chat.chat_id) + " sum_up " + str(t))


def alarm_check_in(context: CallbackContext) -> None:
    """
    提醒每日打卡
    """
    job = context.job
    chat_id = int(job.name.split(" ")[0])
    context.bot.send_message(job.context, text=get_all_users_status(chat_id))
    print("send alarm check in: chat_id - " + str(chat_id))


def alarm_sum_up_yesterday(context: CallbackContext) -> None:
    """
    提醒昨日打卡情況
    """
    job = context.job
    chat_id = int(job.name.split(" ")[0])
    context.bot.send_message(job.context, text=sum_up_yesterday(chat_id))
    print("send sum up: chat_id - " + str(chat_id))


def timing(updater, delay):
    time.sleep(delay)


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


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
        context.job_queue.run_repeating(
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
