# -*- encoding:utf-8 -*-
"""
取引注文を行う
"""

__author__ = "KoYoshizawa <water.9100@gmail.com>"
__version__ = "0.0.1"
__date__ = "01 August 2018"

from decimal import Decimal


class Trader(object):

    ORDER_TABLE = {
        0: {'start': 1},
        1: {'win': 1, 'lose': 9},
        3: {'win': 1, 'lose': 9},
        9: {'win': 3, 'lose': 12},
        12: {'win': 12, 'lose': 3},
    }

    @staticmethod
    def get_long(current_rate: Decimal, prev_coins: int, prev_win_lose: str):
        """
        買いの新規注文
        :param current_rate: 現在の価格
        :param prev_coins: 前回取引の枚数
        :param prev_win_lose: 'win' or 'lose'
        :return position_rate: Decimal 注文時のレート
        :return current_coins: int 注文枚数
        """
        position_rate = current_rate
        current_coins = Trader.ORDER_TABLE[prev_coins][prev_win_lose]
        return position_rate, current_coins

    @staticmethod
    def get_short(current_rate: Decimal, prev_coins: int, prev_win_lose: str):
        """
        売りの新規注文
        :param current_rate: 現在の価格
        :param prev_coins: 前回取引の枚数
        :param prev_win_lose: 'win' or 'lose'
        :return position_rate: Decimal 注文時のレート
        :return current_coins: int 注文枚数
        """
        position_rate = current_rate
        current_coins = Trader.ORDER_TABLE[prev_coins][prev_win_lose]
        return position_rate, current_coins

    @staticmethod
    def settle_long(current_coins: int):
        """
        買いの決済注文
        :param current_coins: 現在の枚数
        :return:
        """
        pass

    @staticmethod
    def settle_short(current_coins: int):
        """
        売りの決済注文
        :param current_coins: 現在の枚数
        :return:
        """
        pass
