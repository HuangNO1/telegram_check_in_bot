from datetime import time


class Chat(object):
    """
    chat 對象代表加入打卡的 chat
    chat_id: tg 所在的群聊 chat id
    alarm_times: 每日提醒時間 e.g. ["10:03:22", "22:22:22"] 時間字符串分別代表時、分、秒
    alarm_days: 每週哪天提醒 e.g. (0,1,2,3,4,5,6)
    sum_up_time: 每日什麼時間點結算昨天的打卡 e.g. "04:00:00"
    enable: 是否啟用通知
    """

    def __init__(self, chat_id: int, alarm_times: list, alarm_days: tuple, sum_up_time: time, enable: bool) -> None:
        self.chat_id = chat_id
        self.alarm_times = alarm_times
        self.alarm_days = alarm_days
        self.sum_up_time = sum_up_time
        self.enable = enable

    def __str__(self):
        return "<chat_id: %s, alarm_times: %s, alarm_days:%s, sum_up_time: %s, enable: %s>" \
            % (self.chat_id, self.alarm_times, self.alarm_days, self.sum_up_time, self.enable)


class User(object):
    """
    user代表有哪些user需要每天打卡
    """

    def __init__(self, chat_id: int, user_id: int, username: str, sum_days: int, continuous_days: int,
                 is_check_in_today: bool, is_check_in_yesterday: bool) -> None:
        self.chat_id = chat_id
        self.user_id = user_id
        self.username = username
        self.sum_days = sum_days
        self.continuous_days = continuous_days
        self.is_check_in_today = is_check_in_today
        self.is_check_in_yesterday = is_check_in_yesterday
    
    def __str__(self):
        return "<chat_id: %s, user_id: %s, username:%s, sum_days: %s, continuous_days: %s, is_check_in_today: %s, is_check_in_yesterday: %s>" \
            % (self.chat_id, self.user_id, self.username, self.sum_days, self.continuous_days, self.is_check_in_today, self.is_check_in_yesterday)
