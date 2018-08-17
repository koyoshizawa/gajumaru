# -*- encoding:utf-8 -*-

from datetime import datetime, time

__author__ = "KoYoshizawa <water.9100@gmail.com>"
__version__ = "0.0.1"
__date__ = "01 August 2018"

class JudgeTradeTime(object):

    def __init__(self, date_time: datetime, product_type=1):
        self.date_time = date_time
        self.product_type = product_type

    def is_trade_time(self) -> bool:
        """
        トレード時間であればTrueを返す
        :return:
        """
        # 月:0 -> 日:6
        mid_night_start_time = time(0, 0, 0, 0)
        day_start_time = time(9, 0, 0, 0)
        day_end_time = time(15, 0, 0, 0)
        night_start_time = time(16, 30, 0, 0)
        night_end_time = time(5, 0, 0, 0)
        mid_night_end_time = time(23, 59, 0, 0)

        # 火 -> 金 は0:00-5:00 9:00-15:00 16:30-24:00
        if 1 <= self.date_time.weekday() <= 4:
            if (mid_night_start_time <= self.date_time.time() <= night_end_time) or \
                    (day_start_time <= self.date_time.time() <= day_end_time) or \
                    (night_start_time <= self.date_time.time() <= mid_night_end_time):
                return True

        # 月は9:00-15:00 16:30-24:00
        elif self.date_time.weekday() == 0:
            if (day_start_time <= self.date_time.time() <= day_end_time) or \
                    (night_start_time <= self.date_time.time() <= mid_night_end_time):
                return True

        # 土は0:00-5:00
        elif self.date_time.weekday() == 5:
            if mid_night_start_time <= self.date_time.time() <= night_end_time:
                return True
