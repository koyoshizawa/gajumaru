from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView
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
    model = HistoricalRate

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


class TradeLogList(ListView):
    """
    取引履歴を表示
    """
    template_name = 'transaction_management/trade_log_list.html'
    paginate_by = 30
    model = TranLog

    def get_context_data(self, *, object_list=None, **kwargs):
        # 始めに継承元のメソッドを呼び出す
        context = super().get_context_data(**kwargs)
        # templateへ渡すデータを整形
        context['info'] = {
            'title': '取引履歴',
            'start_date': self.request.POST['start_date'] if 'start_date' in self.request.POST.keys()
                                                          else '2017-01-01',
            'end_date': self.request.POST['end_date'] if 'end_date' in self.request.POST.keys()
                                                          else '2018-12-31',
        }
        return context

    def get_queryset(self):

        q_start_date = self.request.POST['start-date'] if 'start-date' in self.request.POST.keys() else '2017-01-01'
        q_end_date = self.request.POST['end-date'] if 'end-date' in self.request.POST.keys() else '2018-12-31'

        # 日付型へ変換
        q_start_date = str_date_to_datetime_01(q_start_date)
        q_end_date = str_date_to_datetime_01(q_end_date)

        results = self.model.objects.filter(datetime__range=[q_start_date, q_end_date])
        return results

