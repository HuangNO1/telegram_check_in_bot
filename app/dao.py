"""
dao.py 負責與數據庫的訪問
"""

import os
import configparser
import sqlite3
from data_struct import *
from datetime import time

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
        # list str to datetime.time object
        alarm_times_str = str(row[1]).split(" ")
        alarm_times = []
        for x in alarm_times_str:
            t = x.split(":")
            oj = time(hour=int(t[0]), minute=int(t[1]), second=int(t[2]))
            alarm_times.append(oj)
        alarm_days = tuple(map(str, str(row[2]).split(" ")))
        sum_up_time_str = str(row[3]).split(":")
        sum_up_time = time(
            hour=int(sum_up_time_str[0]), minute=int(sum_up_time_str[1]), second=int(sum_up_time_str[2]))
        enable = row[4]
        temp = Chat(chat_id, alarm_times, alarm_days, sum_up_time, enable)
        chats.append(temp)
    return chats

def get_chat_by_chat_id(chat_id:int) -> Chat:
    """
    根據 chat_id 獲取 chat
    """
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cur = conn.cursor()
    row = cur.execute(
        f"SELECT * FROM chat WHERE chat_id={chat_id}").fetchall()
    conn.commit()
    conn.close()
    if len(row) == 0:
        return None
    chat_id = int(row[0][0])
     # list str to datetime.time object
    alarm_times_str = str(row[0][1]).split(" ")
    alarm_times = []
    for x in alarm_times_str:
        t = x.split(":")
        oj = time(hour=int(t[0]), minute=int(t[1]), second=int(t[2]))
        alarm_times.append(oj)
    alarm_days = tuple(map(str, str(row[0][2]).split(" ")))
    sum_up_time_str = str(row[0][3]).split(":")
    sum_up_time = time(
        hour=int(sum_up_time_str[0]), minute=int(sum_up_time_str[1]), second=int(sum_up_time_str[2]))
    enable = row[0][4]
    res_chat = Chat(chat_id, alarm_times, alarm_days, sum_up_time, enable)
    return res_chat

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
    except Exception as e:
        print(e)
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


def set_chat_alarm_days(chat_id: int, alarm_days: tuple) -> bool:
    """
    設定某 chat 的一週打卡日
    """
    try:
        days_str = " ".join(str(x) for x in alarm_days)
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        cur.execute(
            f"UPDATE chat SET alarm_days=\"{days_str}\" WHERE  chat_id={chat_id}")
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
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
    except Exception as e:
        print(e)
        return False
    return True


def add_chat_alarm(chat_id: int) -> int:
    """
    添加打卡群，預設每週每日都在 12:00:00, 23:00:00 進行打卡提醒，每日 04:00:00 總結昨日打卡情況，啟用打卡。
    因為 chat_id 是 primary key, 所以如果已經存在此打卡群會添加失敗
    如果已經存在 -> 返回 0
    如果不存在且添加成功 -> 返回 1
    如果添加失敗 -> 返回 -1
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        if len(cur.execute(f"SELECT * FROM chat WHERE chat_id={chat_id}").fetchall()) > 0:
            print("this chat is exit")
            return 0
        cur.execute(
            """
            INSERT INTO chat(chat_id, alarm_times, alarm_days, sum_up_time, enable)
            values(?,?,?,?,?)
            """,
            (chat_id, "12:00:00 23:00:00", "0 1 2 3 4 5 6", "04:00:00", True))
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        return -1
    return 1


def remove_chat(chat_id: int) -> bool:
    """
    移除 chat
    如果該群不存在 -> 返回 0
    如果存在且刪除成功 -> 返回 1
    如果刪除失敗 -> 返回 -1
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        # 檢查是否存在
        if len(cur.execute(f"SELECT * FROM chat WHERE chat_id={chat_id}").fetchall()) == 0:
            print("the chat is inexist")
            return 0
        cur.execute(
            f"DELETE FROM chat WHERE chat_id={chat_id}")
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        return -1
    return 1

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
        username = row[2]
        sum_days = int(row[3])
        continuous_days = int(row[4])
        is_check_in_today = row[5]
        is_check_in_yesterday = row[6]
        temp = User(chat_id, user_id, username, sum_days,
                    continuous_days, is_check_in_today, is_check_in_yesterday)
        users.append(temp)
    return users


def get_user_by_id(chat_id: int, user_id: int) -> User:
    """
    透過 chat_id 與 user_id 獲取特定 user 資料
    如果不存在此 user -> 返回 None
    """
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cur = conn.cursor()
    row = cur.execute(
        f"SELECT * FROM user WHERE chat_id={chat_id} and user_id={user_id}").fetchall()
    conn.commit()
    conn.close()
    if len(row) == 0:
        return None
    chat_id = int(row[0][0])
    user_id = int(row[0][1])
    username = row[0][2]
    sum_days = int(row[0][3])
    continuous_days = int(row[0][4])
    is_check_in_today = row[0][5]
    is_check_in_yesterday = row[0][6]
    res_user = User(chat_id, user_id, username, sum_days,
                    continuous_days, is_check_in_today, is_check_in_yesterday)
    return res_user


def add_user_check_in(chat_id:int, user_id:int, username:str) -> int:
    """
    將用戶添加到打卡列表,初始總打卡天數與連續打卡天數皆為 0, 今天是否打卡與昨日是否打卡皆為 False
    如果 user 已經存在 -> 返回 0
    如果添加語法失敗 -> 返回 -1
    如果添加成功 -> 返回 1
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        # check if user in chat is exist
        if len(cur.execute(f"SELECT * FROM user WHERE chat_id={chat_id} and user_id={user_id}").fetchall()) > 0:
            print("the user exist in this chat")
            return 0

        cur.execute(
            """
            INSERT INTO user(chat_id, user_id, username, sum_days, continuous_days, is_check_in_today, is_check_in_yesterday)
            values(?,?,?,?,?,?,?)
            """,
            (chat_id, user_id, username, 0, 0, False, False))
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        return -1
    return 1

def remove_user_from_chat(chat_id: int, user_id: int) -> int:
    """
    移除某群 user 打卡
    如果該群不存在此 user -> 返回 0
    如果存在且刪除成功 -> 返回 1
    如果刪除失敗 -> 返回 -1
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cur = conn.cursor()
        if len(cur.execute(f"SELECT * FROM user WHERE chat_id={chat_id} and user_id={user_id}").fetchall()) == 0:
            print("the user inexist in this chat")
            return 0
        cur.execute(
            f"DELETE FROM user WHERE chat_id={chat_id} and user_id={user_id}")
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        return -1
    return 1


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
            SET is_check_in_today=true,
                sum_days=
                    CASE WHEN is_check_in_today==false
                    THEN sum_days+1
                    ELSE sum_days END,
                continuous_days=
                    CASE WHEN is_check_in_yesterday==true and is_check_in_today==false
                    THEN continuous_days + 1
                    ELSE 1 END
            WHERE 
               chat_id={chat_id} 
               and user_id={user_id}
            """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
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
            SET is_check_in_yesterday=
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
    except Exception as e:
        print(e)
        return False
    return True

def print_list_obj(list_obj: list)->None:
    for x in list_obj:
        print(x)

def test():
    # try:
    chat_id = 66
    username = "chch"
    add_chat_alarm(chat_id)
    chats = get_all_chat()
    print_list_obj(chats)
    print("test get one chat -----")
    chat = get_chat_by_chat_id(chat_id)
    print(chat)
    print("----------------")
    set_chat_alarm_days(chat_id, (0, 3, 4))
    set_chat_alarm_time(chat_id, ["05:00:01", "12:00:02"])
    set_sum_up_time(chat_id, "03:00:20")
    switch_chat_alarm(chat_id, False)
    # except:
    #     print("error")
    #     pass
    chats = get_all_chat()
    print_list_obj(chats)
    for i in range(0, 3):
        add_user_check_in(chat_id, i, username)
    print("\nget all users\n")
    users = get_users_by_chat_id(chat_id)
    print_list_obj(users)
    print("\nget a user\n")
    u = get_user_by_id(chat_id, 1)
    print(u)
    # 打卡
    check_in_today(chat_id, 0)
    check_in_today(chat_id, 1)
    print("\nafter check in, get all users\n")
    users = get_users_by_chat_id(chat_id)
    print_list_obj(users)
    # 檢查昨日打卡
    check_yesterday(chat_id)
    print("\nafter check yesterday, get all users\n")
    users = get_users_by_chat_id(chat_id)
    print_list_obj(users)
    remove_user_from_chat(chat_id, 2)
    print("\nafter remove, get all users\n")
    users = get_users_by_chat_id(chat_id)
    print_list_obj(users)


if __name__ == "__main__":
    test()
