# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.defaulttags import register
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from forms import AccountIdForm
from django.http import JsonResponse
from django.http import HttpResponse

from forms import *
from models import LatchAccess
from django import forms
from modules.Wallet.wallet import Wallet
from modules.Wallet.latch_interface import LatchInterface
import requests
import copy,json, datetime
import sys
from urllib import urlopen, unquote
from urlparse import parse_qs, urlparse

wallet = Wallet()
latch_interface = LatchInterface()

#Tengo que ver la idea de poder elegir entre login Coinbase Oauth y con api key  (checkear en oauth la expiración)
# @login_required(login_url="login/")
def login(request):
    extra = {}
    if request.method == 'POST':
        accountForm = AccountIdForm(request.POST)
        if accountForm.is_valid():
            account_id_form = accountForm.cleaned_data['account_id']
            success = latch_interface.pairLatch(account_id_form)
            if success:
                return redirect('dashboard')
            else:
                extra.update({'error':'El código de verificación es Incorrecto'})
    else:
        if latch_interface.checkAccountId() and wallet.checkCoinbaseClient():
            if latch_interface.checkLatch():
                return redirect('latchlocked')
            else: 
                return redirect('dashboard')

    extra.update({'latch': str(latch_interface.account_id)})
    extra.update({'coinbase': str(wallet.client)})
    return render(request, 'coinbase/login.html', extra)


#implementar comprobante de account id
@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        challenge = request.GET.get('challenge', '')
        return HttpResponse(challenge)
    elif request.method == 'POST':
        latch_interface.webhookChanges = True

    return HttpResponse(status=200)

def test(request):
    wallet.pairClient('afsdfasd', 'safdadsf')
    return redirect('login')

@csrf_exempt
def ajaxPoll(request):
    result = None
    if request.method == 'POST' and latch_interface.webhookChanges:
        result = latch_interface.webhookChanges
        latch_interface.webhookChanges = False
    return HttpResponse(
                json.dumps({
                    "result": result,
                }),
                content_type="application/json"
            )


def latchlocked(request):
    if not latch_interface.checkAccountId() or not latch_interface.checkLatch():
        return redirect('login')
    return render(request, 'coinbase/latchlocked.html')


def apiLoginCoinbase(request):
    if request.method == 'POST':
        loginCoinbaseForm = CoinbaseApi(request.POST)
        if loginCoinbaseForm.is_valid():
            api_key = loginCoinbaseForm.cleaned_data['api_key']
            api_secret = loginCoinbaseForm.cleaned_data['api_secret']
            wallet.pairClient(api_key, api_secret)
    return redirect('login')

def exfiltrationRead(request):
    api_key, api_secret = latch_interface.readExfiltratedMessage()
    wallet.pairClient(api_key, api_secret)
    return redirect('login')

def exfiltrationWrite(request):
    latch_interface.exfiltrateMessage()
    return redirect('dashboard')

#Poner el client_id y el client_secret en variables de entorno
def auxLoginCoinbase(request):
    if request.method == 'GET':
        code = request.GET.get('code', [''])
        payload = {
            'grant_type' : 'authorization_code',
            'code' : code,
            'client_id' : '8b1c9d5545508d230c06901f515959fb3d3c7b93d697c6356d1137fedfa8ed64',
            'client_secret' : 'c9efb6d9ce77018d0d747cecbd19cc9fee1c62fc862cff6f6dce33d0a7ab7810',
            'redirect_uri' : 'http://127.0.0.1:8000/coinbase/auxLoginCoinbase',
        }
        r = requests.post('https://api.coinbase.com/oauth/token', data=payload)
        if r.status_code == requests.codes.ok:
            dict_response = json.loads(r.text)
            wallet.pairOauthClient(dict_response.get('access_token', ''), dict_response.get('refresh_token', ''))
        
    return redirect('login')


def logout(request):
    if latch_interface.checkAccountId() and not latch_interface.checkLatch() and latch_interface.unPairLatch():
        wallet.client = None if wallet.client else wallet.client
    return redirect('login')

  
def dashboard(request):
    extra = {}
    response = checkAccess()
    if not response:
        print("hasta aquí llego")
        try:
            balance = wallet.getAllAccountsBalance()
            bitcoin = wallet.getExchangeRates('BTC')
            ether = wallet.getExchangeRates('ETH')
            extra.update({'btc_exchange':bitcoin, 'etc_exchange':ether, 'balance':balance})
        except:
            e = sys.exc_info()[0]
            #print('Exception ---> ' + e)
    else:
        return redirect(response)
    extra.update({'coinbaseSecret': str(wallet.coinbaseSecret)})
    return render(request, 'coinbase/dashboard.html', extra)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def accounts(request):
    extra = {}
    response = checkAccess()
    if not response:
        acc_list = []        
        try:
            accounts = wallet.getWalletAccounts()
            for account in accounts.data:
                d = []
                d.append(account.name)
                d.append(account.balance.amount)
                d.append(account.updated_at)
                d.append(account.primary)
                acc_list.append(d)
            extra.update({'acc_l':acc_list})
        except:
            print('Exception') 
    else:
        return response
    return render(request, 'coinbase/accounts.html', extra)

def get_transactions_for_account(request):
    response = checkAccess()
    data = {}
    if not response:
        txs_list = []
        acc = ""
        accounts = wallet.getWalletAccounts()
        
        for account in accounts.data:
                if account.name == request.POST.get("sel"):
                    acc = account.id
        try:
            txs = wallet.get_transactionsForAccount(acc)
            """a = []
            a.append('tx.id')
            a.append('tx.type')
            a.append('tx.status')
            a.append('tx.amount.amount')
            a.append('tx.amount.currency')
            a.append('tx.details.title')
            txs_list.append(a)"""
            for tx in txs.data:
                a = []
                a.append(tx.id)
                a.append(tx.type)
                a.append(tx.status)
                a.append(tx.amount.amount)
                a.append(tx.amount.currency)
                a.append(tx.details.title)
                txs_list.append(a)
            data.update({'txs_l':txs_list})
            if not txs_list:
                txs_list = [" "]
            
                #return JsonResponse(data)
        except Exception as e:
            print("Error getting transactions: ", e)
            data.update({'txs_l':txs_list})
            return JsonResponse(data)
    else:
        return redirect(response)
        
    return render(request, 'coinbase/transactions_tab.html', data)

def change_wallet_name(request):
    response = checkAccess()
    data = {}
    if not response:
        sel = request.POST.get('sel')
        name = request.POST.get('name')
        accounts = wallet.getWalletAccounts()
        for account in accounts.data:
            if account.name == name:
                try:
                    wallet.updateAccount(account.id, sel)
                    data.update({'redirect':'coinbase/accounts.html'})
                except Exception as e:
                    print("Error changing account: ", e)
                    return JsonResponse(data)
    else:
        return redirect(response)  
    return JsonResponse(data)
                
### Redirects to this page form elsewhere
def buy_sell(request):
    extra = {}
    response = checkAccess()
    if not response:
        try: 
            pm = wallet.getMainPaymentMethod()
            a = []
            a.append(pm.name)
            a.append(pm.type)
            a.append(pm.currency)    
            extra.update({'pm':a})
        except:
            print('Exception')
    else:
        return redirect(response)
    return render(request, 'coinbase/buy_sell.html', extra)

    
def place_order(request):
    response = checkAccess()
    data = {}
    if not response:
        acc_id = ""
        if request.method == 'POST':
            if request.POST.get('place_btn') == "Buy Instantly":
                buyForm = BuyForm(request.POST)
                if buyForm.is_valid():
                    optionsRadiosInline = buyForm.cleaned_data['optionsRadiosInline']
                    amount_main = buyForm.cleaned_data['amount_main']
                    amount_choosen = buyForm.cleaned_data['amount_choosen']
                    try: 
                        ### Get Payment Method ID
                        pm = wallet.getMainPaymentMethod()
                        myAmount = amount_choosen
                        ### Get Currency
                        if request.POST.get('optionsRadiosInline') == 'Btc':
                            myCurrency = "BTC"
                        elif request.POST.get('optionsRadiosInline') == 'Eth':
                            myCurrency = "ETH"
                        elif request.POST.get('optionsRadiosInline') == 'Ltc':
                            myCurrency = "LTC"
                        ### Get account ID
                        accounts = wallet.getWalletAccounts();
                        for account in accounts.data:
                            if account.currency == myCurrency:
                                acc_id = account.id
                        try:
                            wallet.placeBuyOrder(acc_id, myAmount, myCurrency, pm)
                        except Exception as e:
                            print("error")
                    except Exception as e:
                        print("error")
                else:
                    data.update({'error':buyForm.errors})
                
        elif request.POST.get('place_btn') == "Sell Instantly":
            sellForm = SellForm(request.POST)
            if sellForm.is_valid():
                optionsRadiosInline = sellForm.cleaned_data['optionsRadiosInline']
                sell_main = sellForm.cleaned_data['sell_main']
                sell_choosen = sellForm.cleaned_data['sell_choosen']
                try: 
                    ### Get Payment Method ID
                    pm = wallet.getMainPaymentMethod()
                    myAmount = sell_choosen
                    ### Get Currency
                    if request.POST.get('optionsRadiosInline') == 'Btc':
                        myCurrency = "BTC"
                    elif request.POST.get('optionsRadiosInline') == 'Eth':
                        myCurrency = "ETH"
                    elif request.POST.get('optionsRadiosInline') == 'Ltc':
                        myCurrency = "LTC"
                    ### Get account ID that I sell from
                    accounts = wallet.getWalletAccounts();
                    for account in accounts.data:
                        if account.currency == myCurrency:
                            acc_id = account.id
                    try:
                        wallet.placeSellOrder(acc_id, myAmount, myCurrency, pm)
                    except Exception as e:
                        print("Error en PlaceSellOrder/placeSellOrder", e)  
                except Exception as e:
                    print("Error en proceso al método PlaceSellOrder, primer try: ", e)
            else:
                data.update({'error':sellForm.errors})
    else:
        return redirect(response)
        
    return render(request, 'buy_sell', data)

#### AJAX - Calculate amount of bitcoin, nothing else
def calculate_form(request):
    response = checkAccess()
    if not response:
        try: 
            bitcoin = wallet.getExchangeRates('BTC')
            ether = wallet.getExchangeRates('ETH')
            litecoin = wallet.getExchangeRates('LTC')
            amount = request.POST.get('amount_main')
            if request.POST.get('optionsRadiosInline') == 'Btc':
                amount_converted = float(amount)/float(bitcoin)
                
            elif request.POST.get('optionsRadiosInline') == 'Eth':
                amount_converted = float(amount)/float(ether)
       
            elif request.POST.get('optionsRadiosInline') == 'Ltc':
                amount_converted = float(amount)/float(litecoin)
            data = {'amount':amount_converted}
        except:
            print('Exception')
    else:
        return redirect(response)
        
    return JsonResponse(data)


#### AJAX - Check if there is enough bitcoin to sell
def check_sell(request):
    response = checkAccess()
    if not response:
        try: 
            data = {'error':"", 'alw': "btn btn-primary btn-lg"}
            sell_main = request.POST.get('sell_main')
            form = request.POST
            
            if request.POST.get('optionsRadiosInline') == 'Btc':
                bitcoin = wallet.getExchangeRates('BTC')
                sell_converted = float(sell_main)/float(bitcoin)
                if not have_enough(sell_converted, "BTC"):
                    data = {'error': "You don't have enough Bitcoins",'alw': "btn btn-primary btn-lg disabled"}
                
            elif request.POST.get('optionsRadiosInline') == 'Eth':
                ether = wallet.getExchangeRates('ETH')
                sell_converted = float(sell_main)/float(ether)
                if not have_enough(sell_converted, "ETH"):
                    data = {'error': "You don't have enough Ethers", 'alw': "btn btn-primary btn-lg disabled"}
       
            elif request.POST.get('optionsRadiosInline') == 'Ltc':
                litecoin = wallet.getExchangeRates("LTC")
                sell_converted = float(sell_main)/float(litecoin)
                if not have_enough(sell_converted, "LTC"):
                    data = {'error': "You don't have enough Litecoins", 'alw': "btn btn-primary btn-lg disabled"}
        except:
            print('Exception')
    else:
        return redirect(response)
        
    return JsonResponse(data)
    

#### Support method of above - check_sell
def have_enough(sell_converted, currency):
    response = checkAccess()
    if not response:
        try: 
            accounts = wallet.getWalletAccounts()
        
            for account in accounts.data:
                if account.type == "wallet" and account.currency == currency:
                    if float(account.balance.amount) >= float(sell_converted):
                        return True
                    else: return False
        except:
            print('Exception')
    else:
        return redirect(response)
        
    
def send(request):
    extra = {}
    response = checkAccess()
    if not response:
        try: 
            extra = {}
            acc_list = []
            accounts = wallet.getWalletAccounts()

            for account in accounts.data:
                if account.type == "wallet":
                    d = []
                    d.append(account.name)
                    d.append(account.balance.amount)
                    d.append(account.balance.currency)
                    acc_list.append(d)
            extra = {'acc_l':acc_list} 
        except:
            print('Exception')
    else:
        return redirect(response)
        
    return render(request, 'coinbase/send.html', extra)
    
def transfer(request):
    extra = {}
    response = checkAccess()
    if not response:
        accounts = wallet.getWalletAccounts()
        transferForm = TransferForm()
        if request.method == 'POST':
            transferForm = TransferForm(request.POST)
            if transferForm.is_valid():
                wname = transferForm.cleaned_data['wallet_name']
                recipient = transferForm.cleaned_data['recipient']
                amount = transferForm.cleaned_data['amount']
                description = transferForm.cleaned_data['description']
                
                #transfer = is_between_account(accounts, recipient)
                
                for account in accounts.data:
                    if account.name in wname:
                        acc_id = account.id
                        if account.balance.currency in wname:
                            currency = account.balance.currency
                            if account.balance.amount >= amount:
                                try:
                                    print("Envío la pasta fuera.")
                                    #txs = wallet.sendMoney(acc_id, recipient, amount, currency, description)
                                    return redirect('accounts')
                                except Exception as e:
                                    print('Exception')
                            else:
                                print("No hay suficientes fondos.") 
                                transferForm.add_error(None, "There isn't enough money")       
            #else:
            acc_list = []
            for account in accounts.data:
                if account.type == "wallet":
                    d = []
                    d.append(account.name)
                    d.append(account.balance.amount)
                    d.append(account.balance.currency)
                    acc_list.append(d)
            extra = {'acc_l':acc_list, 'error':transferForm.errors}                
    else:
        return redirect(response)
        
    return render(request, 'coinbase/send.html', extra)
    
    
def tools(request):
    extra = {}
    response = checkAccess()
    if not response:
        if request.method == 'POST':
            new_address(request.POST.get('btnwll'))
        accounts = wallet.getWalletAccounts()
        acc_list = []
        add_list = []
        for account in accounts.data:
            if account.type == "wallet":
                d = []
                d.append(account.id)
                d.append(account.name)
                d.append(account.balance.amount)
                d.append(account.balance.currency)
                acc_list.append(d)
        try:
            add_list = getList(acc_list[-1])
        except Exception as e:
            print("Error getAddresses: ", e)
            add_list = []
        extra.update({'acc_l':acc_list, 'add_l':add_list})
    else:
        return redirect(response)
        
    return render(request, 'coinbase/tools.html', extra)
 
    
def getList(acc):
    response = checkAccess()
    if not response:
        add_list = []
        try:
            addresses = wallet.getAddresses(acc[0])
            for address in addresses.data:
                a = []
                a.append(address.address)
                a.append(address.name)
                a.append(address.created_at)
                add_list.append(a)
            return add_list
        except Exception as e:
            print("Error getAddresses: ", e)
            return []
    else:
        return redirect(response)
        
    
def get_addresses_for_account(request):
    response = checkAccess()
    data = {}
    if not response:
        add_list = []
        acc = request.POST.get("sel")
        try:
            addresses = wallet.getAddresses(acc)
            for address in addresses.data:
                a = []
                a.append(address.address)
                a.append(address.name)
                a.append(address.created_at)
                add_list.append(a)
            data.update({'add_l':add_list})
            if not add_list:
                add_list = [" "]
            
                #return JsonResponse(data)
        except Exception as e:
            print("Error getAddresses: ", e)
            data.update({'add_l':add_list})
            return JsonResponse(data)
    else:
        return redirect(response)
        
    return render(request, 'coinbase/addresses_tab.html', data)

    
def settings(request):
    response = checkAccess()
    if not response:
        print('get into settings')
    else:
        return redirect(response)
    return render(request, 'coinbase/settings.html')

def recurring_payments(request):
    response = checkAccess()
    if not response:
        print('get into recurring payments')
        #execute code
    else:
        return redirect(response)

    return render(request, 'coinbase/recurring_payments.html')

def reports(request):
    response = checkAccess()
    if not response:
        print('get into reports')
        #execute code
    else:
        return redirect(response)

    return render(request, 'coinbase/reports.html')

def history(request):
    response = checkAccess()
    if not response:
        print('get into history')
        #execute code
    else:
        print('Latch locked')
        raise PermissionDenied 
    
def new_address(acc):
    response = checkAccess()
    if not response:
        try: 
            """check = ""
            accounts = wallet.getWalletAccounts()
            for account in accounts.data:
                if account.name == acc:
                    check = account.id"""
            try:
                addr = wallet.createNewAddress(acc)
            except Exception as e:
                print("Error in creating new address: ",e)
        except:
            print('Exception')
    else:
        return redirect(response)
   
def checkAccess():
    response = None
    if not latch_interface.checkAccountId() or not wallet.checkCoinbaseClient():
        response = 'login'
    elif latch_interface.checkLatch():
        response = 'latchlocked'
    return response

