# -*- encoding:utf-8 -*-
from datetime import datetime

from django.core.management.base import BaseCommand
from lib.judge_trade_time import JudgeTradeTime
from lib.chart_monitor import ChartMonitor
from lib.agent import Agent
from lib.scrape_rate import ScrapeRate


class Command(BaseCommand):

    def handle(self, *args, **options):

        # トレードロジック実行
        self.exec_trade()

    @staticmethod
    def exec_trade():
        """
        本番トレード実行
        """

        # トレード時間のみトレードを実行
        now = datetime.now()
        judge_trade_time = JudgeTradeTime(date_time=now)
        if judge_trade_time.is_trade_time():

            # webから現在価格を取得(ついでにDBに格納)
            price = ScrapeRate().get_rate()

            # agent, chart_monitorを初期化
            chart_monitor = ChartMonitor()
            chart_monitor.get_saved_data()  # 最新のデータで更新
            agent = Agent(price)
            agent.get_saved_data()  # 最新のデータで更新

            # 取引の実行
            date_time = datetime.now()
            if chart_monitor.identify_chart(price, date_time):
                has_trade = agent.monitor_transition(chart_monitor.current_rate, chart_monitor.prev_top,
                                                     chart_monitor.prev_bottom, chart_monitor.has_over_top,
                                                     chart_monitor.has_bellow_bottom)

                # 取引記録をデータベースに保存
                agent.save_log(date_time=chart_monitor.datetime, has_trade=has_trade)

            chart_monitor.save_log()
