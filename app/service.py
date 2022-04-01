"""
service.py 負責業務邏輯
"""
from data_struct import *
from datetime import time
from dao import *
from telegram import *
from telegram.ext import *


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
                          conditions_days=user.conditions_days)
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
    for user in users:
        if user.is_check_in_yesterday == True:
            is_check_in += f"@{user.username} "
        else:
            no_check_in += f"@{user.username} "
    is_check_in += "\n> Good Job! 繼續保持~\n\n"
    no_check_in += "\nAre you OK? Fuxk you! 請自主每日打卡!"
    return is_check_in + no_check_in


def get_all_users_status(chat_id: int) -> str:
    """
    獲取該群所有的信息
    """
    users = get_users_by_chat_id(chat_id)
    if len(users) == 0:
        return "此群無使用者需要打卡"
    user_str = "@{username} 你今日{is_check_in_today}，昨日{is_check_in_yesterday}，\
                目前已經累計打卡{sum_days}天，連續打卡{continuous_days}\n"
    res = ""
    for user in users:
        res += user_str.format(
            username=user.username,
            is_check_in_today="已打卡" if user.is_check_in_today else "未打卡",
            is_check_in_yesterday="已打卡" if user.is_check_in_yesterday else "未打卡",
            sum_days=user.sum_days,
            conditions_days=user.conditions_days
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
    res_str = "本群每日打卡時間分別為 " + " ".join(str(x) for x in alarm_times) + \
        "，每週需要打卡的日子是星期 " + " ".join(str(x + 1) for x in alarm_days)


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


def delete_chat(chat_id: int) -> str:
    """
    刪除打卡群
    """
    res = remove_chat(chat_id)
    if res == 0:
        return "此群不存在於打卡群，無效操作。"
    elif res == -1:
        return "此群刪除失敗"
    elif res == 1:
        return "此群刪除成功，今後此群不會接收到打卡提示"
    else:
        return "FUXK"


def change_chat_alarm_time(chat_id: int, alarm_times: list) -> str:
    """
    變更打卡群每日打卡時間
    """
    if set_chat_alarm_time(chat_id, alarm_times):
        return "修改每日打卡時間成功"
    else:
        return "修改每日打卡時間失敗"


def change_chat_alarm_days(chat_id: int, alarm_days: tuple) -> str:
    """
    變更打卡群每週哪天需要打卡
    """
    if set_chat_alarm_days(chat_id, alarm_days):
        return "修改週打卡日期成功"
    else:
        return "修改週打卡日期失敗"


def change_chat_alarm_enable() -> str:
    """
    變換是否啟用群打卡
    """


def add_user(chat_id: int, user_id: int, username: str) -> set:
    """
    添加需要打卡的 user
    """
    res = add_user_check_in(chat_id, user_id, username)
    if res == 0:
        return f"@{username} 你已存在該群打卡列表，無效操作。"
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
