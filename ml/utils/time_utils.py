# -*- coding: utf-8 -*-
"""
@Author  : 玖月
@File    : time_utils.py
@Date    : 2021/8/4 17:50
@Desc    : 
"""
import time
from datetime import timedelta


def get_time_dif(start_time):
    """获取已使用时间"""
    end_time = time.time()
    time_dif = end_time - start_time
    return timedelta(seconds=int(round(time_dif, 2)))
    # return timedelta(milliseconds=time_dif)