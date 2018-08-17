from django.db import models

class ChartMonitorLog(models.Model):
    """
    chart_monitor(agentが取引判断をするだけ価格が変動したかを判断)の履歴
    """
    NAME_CHOICES = ((1, 'NikkeiMiniFuture'), )
    product_name = models.IntegerField(choices=NAME_CHOICES)  # 取引対象の種類(選択)
    current_trend = models.IntegerField()  # -1 下降トレンド 1 上昇トレンド
    prev_rate = models.DecimalField(max_digits=7, decimal_places=2)  # 1つ前のレート
    prev_top = models.DecimalField(max_digits=7, decimal_places=2)   # 直前の山
    prev_bottom = models.DecimalField(max_digits=7, decimal_places=2)   # 直前の谷
    has_bellow_bottom = models.BooleanField()
    has_over_top = models.BooleanField()
    created_at = models.DateTimeField(auto_now=True)


class TranLog(models.Model):
    """
    Agentの活動のログ
    """
    NAME_CHOICES = ((1, 'NikkeiMiniFuture'), )
    product_name = models.IntegerField(choices=NAME_CHOICES)  # 取引対象の種類(選択)
    datetime = models.DateTimeField()  # 日時
    current_status = models.CharField(max_length=1)  # A, B, C or D
    current_position = models.CharField(max_length=10)  # long or short
    current_coins = models.IntegerField()  # 現在の枚数
    current_rate = models.DecimalField(max_digits=7, decimal_places=2)  # 現在のレート
    position_rate = models.DecimalField(max_digits=7, decimal_places=2)  # ポジション獲得時のレート
    prev_top = models.DecimalField(max_digits=7, decimal_places=2)  # 前回の山
    prev_bottom = models.DecimalField(max_digits=7, decimal_places=2)  # 前回の谷
    profit_loss = models.DecimalField(max_digits=7, decimal_places=2)  # 損益
    has_trade = models.BooleanField()  # 取引実行 -> True
    created_at = models.DateTimeField(auto_now=True)


class HistoricalRate(models.Model):
    """
    取得した時系列データを格納
    """
    NAME_CHOICES = ((1, 'NikkeiMiniFuture'), )
    product_name = models.IntegerField(choices=NAME_CHOICES)  # 取引対象の種類(選択)
    date_time = models.DateTimeField()  # 日時
    rate = models.DecimalField(max_digits=7, decimal_places=2)  # レート
    created_at = models.DateTimeField(auto_now=True)