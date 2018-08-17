
# -*- encoding:utf-8 -*-

__author__ = "SosukeMatsunaga <>"
__version__ = "0.0.1"
__date__ = "01 August 2018"

from decimal import Decimal
from datetime import datetime
import urllib.request
from bs4 import BeautifulSoup

from transaction_management.models import HistoricalRate


class ScrapeRate(object):

    def __init__(self, product_name=1):
        self.product_name = product_name
        self.rate = Decimal()

        # 日経MINI
        if self.product_name == 1:
            self.scrape_nikkei_mini_rate()
        else:
            pass

        self.save()

    def scrape_nikkei_mini_rate(self):
        """
        指定したサイトから日経先物MINIの価格を取得する。
        """
        url = 'https://moneybox.jp/futures/detail.php?t=f_nikkei'

        # クローリング
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        html = response.read()

        # スクレイピング
        soup = BeautifulSoup(html, "html.parser")
        a = soup.find(id="cntns_l")
        b = a.find('div', class_='cpny')
        c = b.find('span')
        t = c.text
        future_price = Decimal(t.replace(',', ''))

        self.rate = future_price

    def save(self):
        """
        product_typeに応じて取得した価格をDBに格納する
        """
        d = HistoricalRate(product_name=1, date_time=datetime.now(), rate=self.rate)
        d.save()

    def get_rate(self):
        """
        product_typeに応じて取得した価格を返す
        :return: Decimal
        """
        return self.rate
