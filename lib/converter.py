# -*- encoding: utf-8 -*-

from datetime import datetime

def str_date_to_datetime_01(str_date: str) -> datetime:
    """
    yyyy-mm-dd -> date
    :param str_date:
    :return:
    """
    return datetime.strptime(str_date, '%Y-%m-%d')