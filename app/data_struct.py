from datetime import datetime, date


"""
chat 對象代表加入打卡的 chat
chat_id: tg 所在的群聊 chat id
alarm_times: 每日提醒時間 e.g. ["10:03:22", "22:22:22"] 時間字符串分別代表時、分、秒
alarm_days: 每週哪天提醒 e.g. (0,1,2,3,4,5,6)
sum_up_time: 每日什麼時間點結算昨天的打卡 e.g. "04:00:00"
"""
class chat(object):
    def __init__(self, chat_id: int, alarm_times: list, alarm_days: tuple, sum_up_time: datetime) -> None:
        self.chat_id = chat_id
        self.alarm_times = alarm_times
        self.alarm_days = alarm_days
        self.sum_up_time = sum_up_time

"""
user代表有哪些user需要每天打卡
"""
class user(object):
    def __init__(self, chat_id: int, user_id: int, username: str, sum_days: int, continuous_days: int,
                 is_check_in_today: bool, is_check_in_yesterday: bool) -> None:
        self.chat_id = chat_id
        self.user_id = user_id
        self.username = username
        self.sum_days = sum_days
        self.conditions_days = continuous_days
        self.is_check_in_today = is_check_in_today
        self.is_check_in_yesterday = is_check_in_yesterday

