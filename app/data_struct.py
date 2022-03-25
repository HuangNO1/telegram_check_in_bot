from datetime import datetime, date


class chat(object):
    def __init__(self, chat_id: int, alarm_time: list, alarm_days: tuple, sum_up_time: datetime) -> None:
        self.chat_id = chat_id
        self.alarm_time = alarm_time
        self.alarm_days = alarm_days
        self.sum_up_time = sum_up_time


class user(object):
    def __init__(self, username: str, sum_days: int, continuous_days: int,
     is_punched_card_today: bool, is_punched_card_yesterday: bool) -> None:
        self.username = username
        self.sum_days = sum_days
        self.conditions_days = continuous_days
        self.is_punched_card_today = is_punched_card_today

