# -*- coding:utf-8 -*-

"""
価格の変化を監視する
"""

__author__ = "KoYoshizawa <water.9100@gmail.com>"
__version__ = "0.0.1"
__date__ = "01 August 2018"

from datetime import datetime
from transaction_management.models import ChartMonitorLog


class ChartMonitor (object):

    STANDARD_RATE = 50

    def __init__(self, product_name=1):
        self.product_name = product_name  # 商品名
        self.datetime = datetime.now()  # データの日時
        self.current_trend = 0  # -1 下降トレンド 1 上昇トレンド
        self.current_rate = 0  # 現在のレート
        self.prev_rate = 0  # 1つ前のレート
        self.prev_top = 0  # 直前の山
        self.prev_bottom = 0  # 直前の谷
        self.has_bellow_bottom = False  # 直前の谷を下回った -> True (取引を行うたびにFalseに初期化する必要あり)
        self.has_over_top = False  # 直前の山を上回った -> True (取引を行うたびにFalseに初期化する必要あり)

    def save_log(self):
        """
        現在の状態をDBに保存する。
        """

        d = ChartMonitorLog(current_trend=self.current_trend, prev_rate=self.prev_rate, prev_top=self.prev_top,
                            prev_bottom=self.prev_bottom, has_bellow_bottom=self.has_bellow_bottom,
                            has_over_top=self.has_over_top, product_name=self.product_name)
        d.save()

    def get_saved_data(self):
        """
        テスト実行ではない時はインスタンス変数は初期値となっている。
        最新のデータをDBから取得し、インスタンスをupdateする
        (is_test == False　の時のみ実行)
        """
        d = ChartMonitorLog.objects.all().order_by('-id')
        if len(d) > 0:
            d = d.values()[0]
            self.current_trend = d['current_trend']
            self.prev_rate = d['prev_rate']
            self.prev_top = d['prev_top']
            self.prev_bottom = d['prev_bottom']
            self.has_bellow_bottom = d['has_bellow_bottom']
            self.has_over_top = d['has_over_top']

    def identify_chart(self, current_rate, date_time: datetime) -> bool:
        """
        前回の価格と比較して指定した以上の変動があった場合、
        現在のトレンド、谷、山、直近の谷を下回っているか、直近の谷を上回っているか判断を行う
        :param current_rate: 現在のレート
        :param date_time: 実行日時
        :return: 指定の値以上の変動がある->True ない->False
        """
        # 実行日時をセット
        self.datetime = date_time

        # 現在の価格をセット
        self.current_rate = current_rate

        # 2回目のみ実行 1回目2回目のデータから現在のトレンドを取得する
        if self.prev_rate == 0:
            if self.current_rate > self.prev_rate:
                self.current_trend = 1
            else:
                self.current_rate = -1

        # 価格に指定した値以上の変動があるか
        if self._has_over_standard_rate():

            # 山or谷が発生しているか確認
            # self.current_trend -1 なのに 前回よりも価格が高い -> 前回の価格が谷
            if self.current_trend == -1 and self.prev_rate < self.current_rate:
                self.prev_bottom = self.prev_rate  # 谷の価格をセット
                self.current_trend = 1  # トレンドを上昇トレンドに変更
            # self.current_trend 1 なのに 前回よりも価格が低い -> 前回の価格が山
            elif self.current_trend == 1 and self.prev_rate > self.current_rate:
                self.prev_top = self.prev_rate  # 山の価格をセット
                self.current_trend = -1  # トレンドを下降トレンドに変更

            # 直近の谷を下回っているか、直近の谷を上回っているか判断
            self._check_over_top_below_bottom()

            # 次の判断の為に、現在の価格を前回の価格としてセット
            self.prev_rate = self.current_rate

            # 取引ロジックを実行する
            return True
        # 取引ロジックは実行しない
        self.prev_rate = self.current_rate
        return False

    def _has_over_standard_rate(self)->bool:
        """
        指定した価格よりも変動が大きいかを判断する
        :return: 指定した価格よりも大きい->True
        """
        if abs(self.prev_rate - self.current_rate) > ChartMonitor.STANDARD_RATE:
            return True
        else:
            return False

    def _check_over_top_below_bottom(self):
        """
        直近の谷を下回っているか、直近の谷を上回っているか判断
        """
        if self.current_rate < self.prev_bottom:
            self.has_bellow_bottom = True
        elif self.current_rate > self.prev_top:
            self.has_over_top = True
        else:
            pass

    def init_over_top_below_bottom(self):
        """
        over_top below_bottom を初期化する
        状態C、Dの取引を実行する際に実行
        """
        self.has_over_top = self.has_bellow_bottom = False
