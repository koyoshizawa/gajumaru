# -*- coding:utf-8 -*-

"""
取引アルゴリズムを実行する
"""

__author__ = "KoYoshizawa <water.9100@gmail.com>"
__version__ = "0.0.1"
__date__ = "01 August 2018"

from decimal import Decimal
from datetime import datetime
from .trader import Trader
from transaction_management.models import TranLog


class Agent (object):
    """
    ロジックに基づいてアルゴリズムを選択し、取引を行うためのエージェントクラス
    """

    STATUS_LIST = ['a', 'b', 'c', 'd']
    POSITION_LIST = ['long', 'short']
    STANDARD_RATE = 20
    LOSS_CUT_RATE = 150

    def __init__(self, start_rate, product_name=1):

        self.product_name = product_name
        self.current_status = ''
        self.current_position = ''
        self.current_coins = 0
        self.current_rate = Decimal(start_rate)
        self.position_rate = Decimal(0)
        self.prev_top = start_rate
        self.prev_bottom = start_rate
        self.has_below_bottom = False
        self.has_over_top = False
        self.total_profit = 0
        self.profit_loss = 0

    def get_saved_data(self):
        """
        テスト実行ではない時はインスタンス変数は初期値となっている。
        最新のデータをDBから取得し、インスタンスをupdateする
        :return:
        """
        d = TranLog.objects.order_by('-id')
        if len(d) > 0:
            d = d.values()[0]
            self.current_status = d['current_status']
            self.current_position = d['current_position']
            self.current_coins = d['current_coins']
            self.position_rate = d['position_rate']

    def monitor_transition(self, current_rate: Decimal, prev_top: Decimal, prev_bottom: Decimal,
                           has_over_top: bool, has_below_bottom: bool)->bool:
        """
        値動きを監視し、取引の実行を行う
        :current_rate Decimal: 現在の価格
        :prev_top Decimal: 直前の山
        :prev_bottom Decimal: 直前の谷
        :return: 取引があった場合はTrue ない場合はFalse
        """
        # 情報の更新
        self._update_info(current_rate, prev_top, prev_bottom, has_over_top, has_below_bottom)

        # 取引判断
        if self.current_position != '':  # ポジションを持っていない(最初の取引前)は実行しない
            # TODO 返り値Trueの場合は呼び出し元でchart_monitorのover_top_below_bottom 初期化することをわすれないこと
            return self.__exec_trade()

        else:
            self._first_trade()

        return False

    def __exec_trade(self)->bool:
        """
        現在の状態に合わせて利確or損切りを実施し、次の状態に遷移させる。
        :return: 取引があった場合はTrue ない場合はFalse
        """
        is_trade = False
        win_lose = ''

        # TODO テスト用
        # print('現在の価格{rate} 現在の状態{status} 現在のポジション{position}'
        #       .format(rate=self.current_rate, status=self.current_status, position=self.current_position))
        # print(self.current_rate, self.current_status, self.current_position)
        # TODO settle_longとsettle_shortの判別
        # 現在の状態から利確or損切りを行うべきか判断し、実行する
        if self.current_status == Agent.STATUS_LIST[0]:  # A
            is_trade, win_lose = self._check_status_a()
            if is_trade:
                # ポジション解消
                Trader.settle_long(self.current_coins)

        elif self.current_status == Agent.STATUS_LIST[1]:  # B
            is_trade, win_lose = self._check_status_b()
            if is_trade:
                # ポジション解消
                Trader.settle_short(self.current_coins)

        elif self.current_status == Agent.STATUS_LIST[2]:  # C
            is_trade, win_lose = self._check_status_c()
            if is_trade:
                # ポジション解消
                Trader.settle_long(self.current_coins)

        elif self.current_status == Agent.STATUS_LIST[3]:  # D
            is_trade, win_lose = self._check_status_d()
            if is_trade:
                # ポジション解消
                Trader.settle_short(self.current_coins)

        # ポジションの解消が行われた場合、現在枚数、ポジションレートを初期化し、次の取引ロジックを実行
        if is_trade:
            # TODO テスト用 損益計算を行う
            self._calculate_profit_loss(win_lose)

            # ポジションレートを初期化
            # TODO position_rateは次の取引枚数を設定する為に前回取引枚数を保持する必要がある為、そのまま保持
            self.position_rate = 0
            # 取引の勝ち負けによって次実行するルール確定
            next_status = self._get_acceptable_method_type()[win_lose]

            # 次の取引ルールを実行
            eval('self._change_status_to_{}'.format(next_status))(win_lose)
            # 状態C, Dの取引チェックに使用する情報を初期化
            self.has_over_top = self.has_below_bottom = False

        return is_trade

    def _first_trade(self):
        """
        1回目のトレード用 A or Bを実行する
        """
        if self.current_rate - self.prev_top > Agent.STANDARD_RATE:
            self._change_status_to_a('start')
        elif self.current_rate - self.prev_bottom < -1 * Agent.STANDARD_RATE:
            self._change_status_to_b('start')

    def _check_status_a(self):
        """
        状態Aの時に実行。利確or損切りをするかどうかを判断する。
        :return is_trade bool: ポジション解消を行うべきかの真偽を返す
        :return win_lose str: ポジション解消による勝ち負けを返す 'win', 'lose', 'keep'
        """
        if self.current_rate - self.prev_bottom < -1 * Agent.STANDARD_RATE:
            return True, 'win'
        elif self.current_rate - self.position_rate > Agent.LOSS_CUT_RATE:
            return True, 'lose'
        return False, 'keep'

    def _check_status_b(self):
        """
        状態Bの時に実行。利確or損切りをするかどうかを判断する。
        :return is_trade bool: ポジション解消を行うべきかの真偽を返す
        :return win_lose str: ポジション解消による勝ち負けを返す 'win' 'lose', 'keep'
        """
        if self.current_rate - self.prev_top > Agent.STANDARD_RATE:
            return True, 'win'
        elif self.current_rate - self.position_rate < -1 * Agent.LOSS_CUT_RATE:
            return True, 'lose'
        return False, 'keep'

    def _check_status_c(self):
        """
        状態Cの時に実行。利確or損切りをするかどうかを判断する。
        :return is_trade bool: ポジション解消を行うべきかの真偽を返す
        :return win_lose str: ポジション解消による勝ち負けを返す 'win' 'lose', 'keep'
        """
        # 直近の谷を下回ってから、直近の山を指定の値以上上回る
        if self.has_below_bottom and self.current_rate - self.prev_top > Agent.STANDARD_RATE:
            return True, 'win'
        elif self.current_rate - self.position_rate < -1 * Agent.LOSS_CUT_RATE:
            return True, 'lose'
        return False, 'keep'

    def _check_status_d(self):
        """
        状態Dの時に実行。利確or損切りをするかどうかを判断する。
        :return is_trade bool: ポジション解消を行うべきかの真偽を返す
        :return win_lose str: ポジション解消による勝ち負けを返す 'win' 'lose', 'keep'
        """
        # 直近の山を上回ってから、直近の谷を指定の値以上下回る
        if self.has_over_top and self.current_rate - self.prev_bottom < -1 * Agent.STANDARD_RATE:
            return True, 'win'
        elif self.current_rate - self.position_rate > Agent.LOSS_CUT_RATE:
            return True, 'lose'
        return False, 'keep'

    def _change_status_to_a(self, win_lose):
        """
        状態Aに遷移し、ポジションを持つ
        """
        self.position_rate, self.current_coins = Trader.get_short(self.current_rate, self.current_coins, win_lose)
        self.current_position = Agent.POSITION_LIST[1]  # ショートポジション
        self.current_status = Agent.STATUS_LIST[0]  # A

    def _change_status_to_b(self, win_lose):
        """
        状態Bに遷移し、ポジションを持つ
        """
        self.position_rate, self.current_coins = Trader.get_long(self.current_rate, self.current_coins, win_lose)
        self.current_position = Agent.POSITION_LIST[0]  # ロングポジション
        self.current_status = Agent.STATUS_LIST[1]  # B

    def _change_status_to_c(self, win_lose):
        """
        状態Cに遷移し、ポジションを持つ
        """
        self.position_rate, self.current_coins = Trader.get_long(self.current_rate, self.current_coins, win_lose)
        self.current_position = Agent.POSITION_LIST[0]  # ロングポジション
        self.current_status = Agent.STATUS_LIST[2]  # C

    def _change_status_to_d(self, win_lose):
        """
        状態Dに遷移し、ポジションを持つ
        """
        self.position_rate, self.current_coins = Trader.get_short(self.current_rate, self.current_coins, win_lose)
        self.current_position = Agent.POSITION_LIST[1]  # ショートポジション
        self.current_status = Agent.STATUS_LIST[3]  # D

    def _update_info(self, current_rate: Decimal, prev_top: Decimal, prev_bottom: Decimal,
                     has_over_top: bool, has_below_bottom: bool):
        """
        chart_monitorで判断されたcurrent_rate, prev_top, prev_bottom, has_over_top, has_over_bottomのデータで
        agentインスタンスを更新する
        """
        self.current_rate = current_rate
        self.prev_top = prev_top
        self.prev_bottom = prev_bottom
        self.has_over_top = has_over_top
        self.has_below_bottom = has_below_bottom
        self.profit_loss = 0

    def _get_acceptable_method_type(self)->dict:
        """
        現在の状態から選択可能なロジックを確定させる
        :return: {'win': 勝った時の実行ロジック, 'lose': 負けた時の実行ロジック}
        """
        d = {'win': '', 'lose': ''}

        if self.current_status == Agent.STATUS_LIST[0]:  # A
            d['win'] = Agent.STATUS_LIST[1]  # B
            d['lose'] = Agent.STATUS_LIST[2]  # C

        elif self.current_status == Agent.STATUS_LIST[1]:  # B
            d['win'] = Agent.STATUS_LIST[0]  # A
            d['lose'] = Agent.STATUS_LIST[3]  # D

        elif self.current_status == Agent.STATUS_LIST[2]:  # C
            d['win'] = Agent.STATUS_LIST[0]  # A
            d['lose'] = Agent.STATUS_LIST[3]  # D

        elif self.current_status == Agent.STATUS_LIST[3]:  # D
            d['win'] = Agent.STATUS_LIST[1]  # B
            d['lose'] = Agent.STATUS_LIST[2]  # C

        return d

    def _calculate_profit_loss(self, win_lose):
        """
        利確 or 損切り のたびに損益を計算する
        """
        profit_loss = abs(self.current_rate - self.position_rate) * self.current_coins
        if win_lose == 'win':
            self.total_profit = self.total_profit + profit_loss
            self.profit_loss = profit_loss
        else:
            self.total_profit = self.total_profit - profit_loss
            self.profit_loss = -1 * profit_loss

    def save_log(self, date_time: datetime, has_trade: bool):
        """
        取引ログをデータベースに保存
        : unit_id : バックテスト実行時に同一の実行ログを管理するためのID(実行開始時のdatetime)(バックテスト時のみ必要)
        : datetime: 取引を行った時間
        : has_trade: 取引を実行した->True
        : is_test: テスト実行->True
        """
        d = TranLog(datetime=date_time, current_status=self.current_status,
                    current_position=self.current_position, current_coins=self.current_coins,
                    current_rate=self.current_rate, position_rate=self.position_rate,
                    prev_top=self.prev_top, prev_bottom=self.prev_bottom, has_trade=has_trade,
                    profit_loss=self.profit_loss, product_name=self.product_name)
        d.save()
