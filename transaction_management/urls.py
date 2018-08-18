from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import index, historical_data_list, tran_log_list

app_name = 'transaction_management'

urlpatterns = [
    path('historical_data_list/', historical_data_list, name='historical_data_list'),
    path('tran_log_list/', tran_log_list, name='tran_log_list'),
]