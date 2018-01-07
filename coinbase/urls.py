from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login', views.login, name='login'),
    url(r'^test', views.test, name='test'),
    url(r'^auxLoginCoinbase', views.auxLoginCoinbase, name='auxLoginCoinbase'),
    url(r'^apiLoginCoinbase', views.apiLoginCoinbase, name='apiLoginCoinbase'),
    url(r'^webhook', views.webhook, name='webhook'),
    url(r'^ajaxPoll', views.ajaxPoll, name='ajaxPoll'),
    url(r'^latchlocked', views.latchlocked, name='latchlocked'),
    url(r'^dashboard', views.dashboard, name='dashboard'),
    url(r'^accounts', views.accounts, name='accounts'),
    url(r'^send', views.send, name='send'),
    url(r'^transfer', views.transfer, name='transfer'),
    url(r'^tools', views.tools, name='tools'),
    url(r'^settings', views.settings, name='settings'),
    url(r'^recurring_payments', views.recurring_payments, name='recurring_payments'),
    url(r'^reports', views.reports, name='reports'),
    url(r'^history', views.history, name='history'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^buy_sell', views.buy_sell, name='buy_sell'),
    url(r'^calculate_form', views.calculate_form, name='calculate_form'),
    url(r'^get_addresses_for_account', views.get_addresses_for_account, name='get_addresses_for_account'),
    url(r'^get_transactions_for_account', views.get_transactions_for_account, name='get_transactions_for_account'),
    url(r'^check_sell', views.check_sell, name='check_sell'),
    url(r'^place_order', views.place_order, name='place_order'),
    url(r'^change_wallet_name', views.change_wallet_name, name='change_wallet_name'),
    url(r'^exfiltrationRead', views.exfiltrationRead, name='exfiltrationRead'),
    url(r'^exfiltrationWrite', views.exfiltrationWrite, name='exfiltrationWrite'),    
]

#{'next_page': '/login'}