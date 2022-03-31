"""
service.py 負責業務邏輯
"""
from data_struct import *
from datetime import time
from dao import *


def get_user_info(chat_id: int, user_id: int)->None:
    """
    獲取某 user 當前打卡情況
    """
    user = get_user_by_id(chat_id, user_id)
    res = f"@"


