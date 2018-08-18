from django.http import JsonResponse
from django.shortcuts import render
from .models import HistoricalRate, TranLog
from lib.converter import str_date_to_datetime_01

def index(request):
    """
    application top page
    :param request:
    :return:
    """
    template_name = 'transaction_management/index.html'
    return render(request, template_name)

def historical_data_list(request):
    """
    時系列データを表示
    """
    template_name = 'transaction_management/historical_data_list.html'

    # ajaxの場合は、フィルター条件に適うデータをJSONで返す
    if request.is_ajax():

        # パラメータ取得
        start_date = str_date_to_datetime_01(request.GET.get("start_date"))
        end_date = str_date_to_datetime_01(request.GET.get('end_date'))
        product_name = int(request.GET.get('product_name'))

        # 取得パラメータでフィルター
        query_set = HistoricalRate.objects.filter(date_time__range=(start_date, end_date), product_name=product_name)

        # データ整形
        data_set = [{'product_name': q.get_product_name_display(), 'date_time': q.date_time, 'rate': q.rate} for q in query_set]

        return JsonResponse({'data_set': data_set})

    else:
        info = {'title': '時系列データ'}

        return render(request, template_name, info)


def tran_log_list(request):
    """
    取引履歴を表示
    """
    template_name = 'transaction_management/tran_log_list.html'

    # ajaxの場合は、フィルター条件に適うデータをJSONで返す
    if request.is_ajax():

        # パラメータ取得
        start_date = str_date_to_datetime_01(request.GET.get("start_date"))
        end_date = str_date_to_datetime_01(request.GET.get('end_date'))
        product_name = int(request.GET.get('product_name'))

        # 取得パラメータでフィルター
        query_set = TranLog.objects.filter(datetime__range=(start_date, end_date), product_name=product_name)

        # データ整形
        data_set = [{'product_name':q.product_name,
                     'date_time': q.datetime,
                     'rate': q.current_rate,
                     'status': q.current_status,
                     'position': q.current_position,
                     'profit_loss': q.profit_loss,
                     'has_trade': q.has_trade,
                     } for q in query_set]

        return JsonResponse({'data_set': data_set})

    else:
        info = {'title': '取引履歴'}
        return render(request, template_name, info)
