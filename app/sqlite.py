import os
import configparser
import sqlite3
from data_struct import *

config = configparser.ConfigParser()
config.optionxform = str
config.read("../settings.ini")
SQLITE_DB_PATH = os.getcwd()
SQLITE_DB_FILE = config['data']['DB_FILE']


"""
獲取所有 chat
"""
def get_all_chat() -> list:
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM chat").fetchall()
    conn.commit()
    conn.close()
    chats = []
    for row in result:
        chat_id = int(row[0])
        alarm_times = str(rows[1]).split(",")
        alarm_days = tuple(map(str, str(row[2]).split(",")))
        sum_up_time = str(row[3])
        temp = chat(chat_id, alarm_times, alarm_days, sum_up_time)
        chats.append(temp)
    return chats

"""
透過 chat id 獲取所有該 chat 下需要打卡的 user 資料
"""
def get_users_by_chat_id(chat_id: int) -> list:
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cur = conn.cursor()
    result = cur.execute(f"SELECT * FROM user WHERE chat_id={chat_id}").fetchall()
    conn.commit()
    conn.close()
    users = []
    for row in result:
        chat_id = int(row[0])
        user_id = int(row[1])
        username = int(row[2])
        sum_days = int(row[3])
        continuous_days = int(row[4])
        is_check_in_today = row[5]
        is_check_in_yesterday = row[6]
        temp = user(chat_id, user_id, username, sum_days, continuous_days, is_check_in_today, is_check_in_yesterday)
        users.append(temp)
    return users


"""
透過 chat_id 與 user_id 獲取特定 user 資料
"""
def get_user_by_id(chat_id: int, user_id: int) -> user:
    pass


"""
user 打卡某群
"""
def check_in_today(chat_id: int, user_id: int) -> bool:
    pass


"""
chat 是否啟用提醒
"""
def switch_chat_alarm(chat_id: int, is_alarm: bool) -> bool:
    pass


"""
移除 chat
"""
def remove_chat(chat_id: int)->bool:
    pass


"""
移除某群 user 打卡
"""
def remove_user_from_chat(chat_id: int, user_id: int)->bool:
    pass


"""
設定某 chat 的提醒打卡時段
"""
def set_chat_alarm_time(chat_id: int, s: list)->bool:
    pass


"""
設定某 chat 的一週打卡日
"""
def set_chat_alarm_days(chat_id, alarm_days: tuple)->bool:
    pass


"""
檢查並更新昨日的打卡狀況，返回昨日未打卡的 user
"""
def check_yesterday()->list:
    pass
