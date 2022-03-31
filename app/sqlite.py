import os
import configparser
import sqlite3
from data_struct import *
from datetime import datetime, date, time

config = configparser.ConfigParser()
config.optionxform = str
config.read("../settings.ini")
SQLITE_DB_PATH = os.getcwd()
SQLITE_DB_FILE = config['data']['DB_FILE']

# Chat


def get_all_chat() -> list:
    """
    獲取所有 chat
    """
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM chat").fetchall()
    conn.commit()
    conn.close()
    chats = []
    for row in result:
        chat_id = int(row[0])
        alarm_times = str(rows[1]).split(" ")
        alarm_days = tuple(map(str, str(row[2]).split(" ")))
        sum_up_time = str(row[3])
        temp = chat(chat_id, alarm_times, alarm_days, sum_up_time)
        chats.append(temp)
    return chats


def set_chat_alarm_time(chat_id: int, alarm_times: list) -> bool:
    """
    設定某 chat 的提醒打卡時段
    """
    try:
        time_str = ""
        for time in alarm_times:
            time_str += str(time) + " "
        time_str = time_str[:-1]
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        cur.execute(
            f"UPDATE chat SET alarm_times=\"{time_str}\" WHERE  chat_id={chat_id}")
        conn.commit()
        conn.close()
    except:
        return False
    return True


def set_sum_up_time(chat_id: int, sum_up_time: time) -> bool:
    """
    設置每日總結昨日打卡情況時間
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        cur.execute(
            f"UPDATE chat SET sum_up_time=\"{str(sum_up_time)}\" WHERE  chat_id={chat_id}")
        conn.commit()
        conn.close()
    except:
        return False
    return True


def set_chat_alarm_days(chat_id, alarm_days: tuple) -> bool:
    """
    設定某 chat 的一週打卡日
    """
    try:
        days_str = " ".join(str(x) for x in t)
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        cur.execute(
            f"UPDATE chat SET alarm_days=\"{days_str}\" WHERE  chat_id={chat_id}")
        conn.commit()
        conn.close()
    except:
        return False
    return True


def switch_chat_alarm(chat_id: int, is_alarm: bool) -> bool:
    """
    chat 是否啟用提醒
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        cur.execute(
            f"UPDATE chat SET enable={str(is_alarm)} WHERE  chat_id={chat_id}")
        conn.commit()
        conn.close()
    except:
        return False
    return True


def add_chat_alarm(chat_id: int) -> bool:
    """
    添加打卡群，預設每週每日都在 12:00:00, 23:00:00 進行打卡提醒，每日 04:00:00 總結昨日打卡情況，啟用打卡。
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO chat(chat_id, alarm_times, alarm_days, sum_up_time, enable)
            values(?,?,?,?,?)
            """,
            (chat_id, "12:00:00 23:00:00", "0 1 2 3 4 5 6", "04:00:00", True))
        conn.commit()
        conn.close()
    except:
        return False
    return True


def remove_chat(chat_id: int) -> bool:
    """
    移除 chat
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        cur.execute(
            f"DELETE FROM chat SET WHERE chat_id={chat_id}")
        conn.commit()
        conn.close()
    except:
        return False
    return True

# User


def get_users_by_chat_id(chat_id: int) -> list:
    """
    透過 chat id 獲取所有該 chat 下需要打卡的 user 資料
    """
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cur = conn.cursor()
    result = cur.execute(
        f"SELECT * FROM user WHERE chat_id={chat_id}").fetchall()
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
        temp = user(chat_id, user_id, username, sum_days,
                    continuous_days, is_check_in_today, is_check_in_yesterday)
        users.append(temp)
    return users


def get_user_by_id(chat_id: int, user_id: int) -> user:
    """
    透過 chat_id 與 user_id 獲取特定 user 資料
    """
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cur = conn.cursor()
    result = cur.execute(
        f"SELECT * FROM user WHERE chat_id={chat_id} and user_id={user_id}").fetchall()
    conn.commit()
    conn.close()
    chat_id = int(row[0][0])
    user_id = int(row[0][1])
    username = int(row[0][2])
    sum_days = int(row[0][3])
    continuous_days = int(row[0][4])
    is_check_in_today = row[0][5]
    is_check_in_yesterday = row[0][6]
    res_user = user(chat_id, user_id, username, sum_days,
                    continuous_days, is_check_in_today, is_check_in_yesterday)
    return res_user


def check_in_today(chat_id: int, user_id: int) -> bool:
    """
    user 打卡某群,判斷user昨日是否打卡,如果已打卡連續打卡天數(continuous_days + 1),
    否則不 +1 置為 1;累計打卡天數 +1,今日是否打卡置true
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        cur.execute(
            f"""
            UPDATE user 
            SET sum_days=sum_days+1,
                is_check_in_today=true,
                continuous_days=
                    CASE WHEN is_check_in_yesterday==true
                    THEN continuous_days + 1
                    ELSE 1 END
            WHERE 
               chat_id={chat_id} 
               and user_id={user_id}
            """)
        conn.commit()
        conn.close()
    except:
        return False
    return True


def remove_user_from_chat(chat_id: int, user_id: int) -> bool:
    """
    移除某群 user 打卡
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        cur.execute(
            f"DELETE FROM user SET WHERE chat_id={chat_id} and user_id={user_id}")
        conn.commit()
        conn.close()
    except:
        return False
    return True


def check_yesterday(chat_id: int) -> bool:
    """
    檢查並更新昨日的打卡狀況
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        # 將今日已打卡轉變到昨日已打卡
        cur.execute(
            f"""
            UPDATE user 
            SET sum_days=sum_days+1,
                is_check_in_yesterday=
                    CASE WHEN is_check_in_today==true
                    THEN true ELSE false END
            WHERE 
                chat_id={chat_id} 
            """)
        # 將所有今日已打卡皆置為 false
        cur.execute(
            f"""
            UPDATE user
            SET is_check_in_today=false
            WHERE
                chat_id={chat_id}
            """)
        conn.commit()
        conn.close()
    except:
        return False
    return True

# if __name__=="__main__":
#     pass
