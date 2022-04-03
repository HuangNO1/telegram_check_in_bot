"""
service.py 負責業務邏輯，與 job_queue
"""
from data_struct import *
from datetime import time
from dao import *
from telegram import *
from telegram.ext import *


def start_all_chats_jobs(disp: Dispatcher) -> None:
    """
    將所有打卡需要 job 的任務運行起來
    """
    chats = get_all_chat()

    for chat in chats:
        if chat.enable:
            start_chat_jobs(chat, disp)


def start_chat_jobs(chat: Chat, context: CallbackContext) -> None:
    """
    單個打卡群
    啟用
    """
    # 移除舊的 job
    stop_chat_jobs(chat, context)

    # 處理提醒打卡部份
    for t in chat.alarm_times:
        # 運行所有時間段 提示打卡
        context.job_queue.run_daily(
            alarm_check_in, t, chat.alarm_days,
            context=chat.chat_id,
            name=str(chat.chat_id) + " alarm " + str(t))

    # 處理每日總結部份
    # 運行總結昨日打卡
    context.job_queue.run_daily(
        alarm_sum_up_yesterday, chat.sum_up_time, chat.alarm_days,
        context=chat.chat_id,
        name=str(chat.chat_id) + " sum_up " + str(chat.sum_up_time))


def stop_chat_jobs(chat: Chat, context: CallbackContext) -> None:
    """
    單個打卡群
    刪除打卡群 或 是否啟用通知(enable) 變更後 移除舊的 job 任務
    """
    for t in chat.alarm_times:
        job_removed = remove_job_if_exists(
            str(chat.chat_id) + " alarm " + str(t), context)
    remove_job_if_exists(
        str(chat.chat_id) + " sum_up " + str(chat.sum_up_time), context)


def stop_chat_one_job(chat_id: int, opt: str, t: time, context: CallbackContext) -> None:
    """
    chat_id: chat_id
    opt: 代表是 " alarm " 還是 " sum_up "
    t: 代表是哪個時間
    當每日提醒時間(alarm_times) 或 每週提醒天數(alarm_days)
    變更後 移除舊的 job 任務
    """
    remove_job_if_exists(
        str(chat_id) + opt + str(t), context)


def start_chat_one_job(chat_id: int, opt: str,
                       t: time, days: tuple, context: CallbackContext) -> None:
    """
    chat_id: chat_id
    opt: 代表是 " alarm " 還是 " sum_up "
    t: 代表是哪個時間
    days: 每週哪天
    單個打卡群
    當每日提醒時間(alarm_times) 或 每週提醒天數(alarm_days)
    變更後 啟用新的 job 任務
    """
    if opt == " alarm ":
        context.job_queue.run_daily(alarm_check_in, t, days,
                                    context=chat_id, name=str(chat_id) + opt + str(t))
    elif opt == " sum_up ":
        context.job_queue.run_daily(alarm_sum_up_yesterday, t, days,
                                    context=chat_id, name=str(chat_id) + opt + str(t))


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
    print(f"remove job \"{name}\" successfully")
    return True

# -----------------------------------------------------------------------------------------


def get_user_status(chat_id: int, user_id: int) -> str:
    """
    獲取某 user 當前打卡情況
    """
    user = get_user_by_id(chat_id, user_id)
    if user == None:
        return "你在此群未添加打卡！"
    user_str = "@{username} 你今日{is_check_in_today}，目前已經累計打卡{sum_days}天，連續打卡{continuous_days}"
    res = user_str.format(username=user.username,
                          is_check_in_today="已打卡" if user.is_check_in_today else "未打卡，請盡快打卡",
                          sum_days=user.sum_days,
                          continuous_days=user.continuous_days)
    return res


def sum_up_yesterday(chat_id: int) -> str:
    """
    總結昨日打卡情況
    """
    check_yesterday(chat_id)
    users = get_users_by_chat_id(chat_id)
    if len(users) == 0:
        return "此群無使用者需要打卡"
    # 統計昨日未打卡 user
    is_check_in = "昨日已打卡使用者： "
    no_check_in = "昨日未打卡使用者： "
    is_check_in_has_user = False
    no_check_in_has_user = False
    for user in users:
        if user.is_check_in_yesterday == True:
            is_check_in_has_user = True
            is_check_in += f"@{user.username} "
        else:
            no_check_in_has_user = True
            no_check_in += f"@{user.username} "
    if is_check_in_has_user:
        is_check_in += "\n> Good Job! 繼續保持~\n\n"
    else:
        is_check_in = ""
    if no_check_in_has_user:
        no_check_in += "\nAre you OK? Fuxk you! 請自主每日打卡!"
    else:
        no_check_in = ""

    return is_check_in + no_check_in


def get_all_users_status(chat_id: int) -> str:
    """
    獲取該群所有的信息
    """
    users = get_users_by_chat_id(chat_id)
    if len(users) == 0:
        return "此群無使用者需要打卡"
    user_str = "@{username} 你今日{is_check_in_today}，昨日{is_check_in_yesterday}，"\
        "目前已經累計打卡{sum_days}天，連續打卡{continuous_days}\n"
    res = ""
    for user in users:
        res += user_str.format(
            username=user.username,
            is_check_in_today="已打卡" if user.is_check_in_today else "未打卡",
            is_check_in_yesterday="已打卡" if user.is_check_in_yesterday else "未打卡",
            sum_days=user.sum_days,
            continuous_days=user.continuous_days
        )

    res += "\n未打卡的使用者請盡快完成打卡"
    return res


def get_chat_status(chat_id: int) -> str:
    """
    獲取 chat 資訊
    """
    chat = get_chat_by_chat_id(chat_id)
    if chat == None:
        return "本群沒有打卡服務"
    # print(list(chat.alarm_days))
    res_str = "本群每日打卡提醒時間分別為 " + " ".join(str(x) for x in chat.alarm_times) + \
        "\n每週需要打卡的日子是星期 " + " ".join(str(x + 1) for x in list(chat.alarm_days)) + \
        "\n每日總結昨日打卡時間為 " + str(chat.sum_up_time) + "\n\n本群"
    res_str += "已啟用打卡通知" if chat.enable == True else "未啟用打卡通知"
    return res_str


def add_chat(chat_id: int) -> str:
    """
    添加至打卡群
    """
    res = add_chat_alarm(chat_id)
    if res == 0:
        return "此群已存在於打卡群，無效操作。"
    elif res == -1:
        return "此群添加失敗"
    elif res == 1:
        return "此群添加成功"
    else:
        return "FUXK"


def delete_chat(chat_id: int, context: CallbackContext) -> str:
    """
    刪除打卡群
    """
    # 先獲取到當前的 chat
    cur_chat = get_chat_by_chat_id(chat_id)

    res = remove_chat(chat_id)
    if res == 0:
        return "此群不存在於打卡群，無效操作。"
    elif res == -1:
        return "此群刪除失敗"
    elif res == 1:
        # 刪除舊的
        stop_chat_jobs(cur_chat, context)
        return "此群刪除成功，今後此群不會接收到打卡提示"
    else:
        return "FUXK"


def change_chat_alarm_time(chat_id: int, alarm_times: list, context: CallbackContext) -> str:
    """
    變更打卡群每日打卡時間
    如果變更到 alarm_times 因為需要刪除所有的 job 如果你剛好在提醒的時間點進行變更每週情況，會造成無法接收到提醒
    """
    # 先獲取到當前的 chat
    cur_chat = get_chat_by_chat_id(chat_id)

    res = set_chat_alarm_time(chat_id, alarm_times)
    if res == 0:
        return "此群不存在於打卡群，無效操作。"
    elif res == -1:
        return "修改每日打卡時間失敗"
    elif res == 1:
        # 獲取到新的 chat
        new_chat = get_chat_by_chat_id(chat_id)
        # 刪除舊的
        for t in cur_chat.alarm_times:
            stop_chat_one_job(cur_chat.chat_id, " alarm ",
                              t, context)
        # 運行新的
        for t in new_chat.alarm_times:
            start_chat_one_job(new_chat.chat_id, " alarm ", t,
                               new_chat.alarm_days, context)
        return "修改每日打卡時間成功"
    else:
        return "FUXK"


def change_chat_alarm_days(chat_id: int, alarm_days: tuple, context: CallbackContext) -> str:
    """
    變更打卡群每週哪天需要打卡
    如果變更到 alarm_days 因為需要刪除所有的 job 如果你剛好在提醒的時間點進行變更每週情況，會造成無法接收到提醒
    """
    # 先獲取到當前的 chat
    cur_chat = get_chat_by_chat_id(chat_id)

    res = set_chat_alarm_days(chat_id, alarm_days)
    if res == 0:
        return "此群不存在於打卡群，無效操作。"
    elif res == -1:
        return "修改週打卡日期失敗"
    elif res == 1:
        # 獲取到新的 chat
        new_chat = get_chat_by_chat_id(chat_id)
        # 刪除舊的
        stop_chat_jobs(cur_chat, context)
        # 運行新的
        start_chat_jobs(new_chat, context)
        return "修改週打卡日期成功"
    else:
        return "FUXK"


def change_chat_sum_up_time(chat_id: int, sum_up_time: str, context: CallbackContext) -> str:
    """
    變更每日總結昨日打卡時間
    """
    # 先獲取到當前的 chat
    cur_chat = get_chat_by_chat_id(chat_id)

    res = set_sum_up_time(chat_id, sum_up_time)
    if res == 0:
        return "此群不存在於打卡群，無效操作。"
    elif res == -1:
        return "修改每日總結昨日打卡時間失敗"
    elif res == 1:
        # 獲取到新的 chat
        new_chat = get_chat_by_chat_id(chat_id)
        # 刪除舊的
        stop_chat_one_job(chat_id, " sum_up ", cur_chat.sum_up_time, context)
        # 運行新的
        start_chat_one_job(chat_id, " sum_up ", new_chat.sum_up_time,
                           new_chat.alarm_days, context)
        return "修改每日總結昨日打卡時間成功"
    else:
        return "FUXK"


def change_chat_alarm_enable(chat_id: int, is_alarm: bool, context: CallbackContext) -> str:
    """
    變換是否啟用群打卡
    """
    # 先獲取到當前的 chat
    cur_chat = get_chat_by_chat_id(chat_id)
    if cur_chat.enable == is_alarm:
        return "當前參數與修改參數相同，無效操作。"

    res = switch_chat_alarm(chat_id, is_alarm)
    if res == 0:
        return "此群不存在於打卡群，無效操作。"
    elif res == -1:
        return "修改是否啟用失敗"
    elif res == 1:
        # 獲取到新的 chat
        new_chat = get_chat_by_chat_id(chat_id)
        txt = "此群今後會接收到打卡通知" if new_chat.enable else "此群今後不會接收到打卡通知"
        # 如果沒有變化
        if cur_chat.enable == new_chat.enable:
            return "修改是否啟用成功且修改無變化。" + txt
        # 如果有變化
        if new_chat.enable:
            start_chat_jobs(new_chat, context)
        else:
            stop_chat_jobs(new_chat, context)

        return "修改是否啟用成功。" + txt
    else:
        return "FUXK"


def add_user(chat_id: int, user_id: int, username: str) -> set:
    """
    添加需要打卡的 user
    """
    res = add_user_check_in(chat_id, user_id, username)
    if res == 0:
        return f"@{username} 你已存在該群打卡列表或此群不存在打卡群列表，無效操作。"
    elif res == -1:
        return f"@{username} 你添加進打卡列表失敗。"
    elif res == 1:
        return f"@{username} 你成功添加進打卡列表成功，今後記得在該群打卡！"
    else:
        return "FUXK"


def check_in(chat_id: int, user_id: int) -> str:
    """
    使用者今日打卡
    """
    if check_in_today(chat_id, user_id):
        return get_user_status(chat_id, user_id)
    else:
        return "打卡失敗"


def delete_user(chat_id: int, user_id: int, username: str) -> str:
    """
    刪除 user 打卡
    """
    res = remove_user_from_chat(chat_id, user_id)
    if res == 0:
        return f"@{username} 你未存在該群打卡列表，無效操作。"
    elif res == -1:
        return f"@{username} 你刪除於打卡列表失敗"
    elif res == 1:
        return f"@{username} 你刪除於打卡列表成功，今後不需要在該群打卡！"
    else:
        return "FUXK"
