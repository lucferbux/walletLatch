# -*- coding: utf-8 -*-
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from Coinbase.coinbase.wallet.client import OAuthClient
from Coinbase.coinbase.wallet.client import Client
from pprint import pprint
# from error import Error
# from Latch import *
import json
import time
import binascii
from latch_interface import LatchInterface


class Wallet(object):

    # VARIABLES & PROPERTIES ------------------------------------------------------------
    
    @property
    def client(self):
        return self._client
    
    @client.setter
    def client(self, client_new):
        self._client = client_new
    

    @property
    def coinbaseKey(self):
        return self._coinbaseKey
    
    @coinbaseKey.setter
    def coinbaseKey(self, coinbaseKey_new):
        self._coinbaseKey = coinbaseKey_new
    
    @property
    def coinbaseSecret(self):
        return self._coinbaseSecret
    
    @coinbaseSecret.setter
    def coinbaseSecret(self, coinbaseSecret_new):
        self._coinbaseSecret = coinbaseSecret_new


    # INIT METHODS ----------------------------------------------------------------------

    def __init__(self):
        self.client = None
        self.coinbaseKey = None
        self.coinbaseSecret = None
        self.latch = LatchInterface()
        

    def checkCoinbaseClient(self):
        return self.client


    # COINBASE METHODS -----------------------------------------------------------------------------------------
    
    def pairOauthClient(self, access_token, refresh_token):
        if not self.client:
            self.client = OAuthClient(access_token, refresh_token)
    
    def pairClient(self, api_key, api_secret):
        print('Entro en pair client con ' + api_key + ' y ' + api_secret)
        self.coinbaseKey = api_key
        self.coinbaseSecret = api_secret
        self.client = Client(api_key, api_secret)


    def getWalletAccounts(self):
        return self.client.get_accounts()

    def getCurrencies(self):
        return self.client.get_currencies()   

    def getCurrentUser(self):
        user = self.client.get_current_user()
        user_json = json.dumps(user)
        print(user_json)
                    
    ######## can be changed: name, time zone, native currency/https://developers.coinbase.com/api/v2?python#update-current-user        
    def updateCurrentUser(self, myname):
        user = self.client.update_current_user(name=myname)
        user_json = json.dumps(user)
        print(user_json)
        

    ######### No la veo en la API anymore, wtf
    def getPrimaryAccount(self):
        account = None
        account = self.client.get_primary_account()
        return account
        
    def createNewBitcoinAccount(self, myname):
        account = self.client.create_account(name=myname)
        balance = account.balance
        print("%s: %s %s" % (account.name, balance.amount, balance.currency))
        print(account.get_transactions())
      
    def updateAccount(self, acc_id, newName):
        account = self.client.update_account(acc_id, name=newName)
        print("AAAAAAAAAAAAAAA: ", account)
        
    ########## Capturar error si se intenta borrar la primary account      
    def deleteAccount(self, acc_id):
        #can't be primary, can't be non-zero, can't be fiat acc, can't be in a vault with pending
        account = self.client.delete_account(acc_id)
            
    def createNewAddress(self, acc_id):
        return self.client.create_address(acc_id)
    
    def getAddresses(self, acc_id):
        addresses = self.client.get_addresses(acc_id)
        return addresses

    def getOneAddresses(self, acc_id, add_id):
        address = self.client.get_address(acc_id, add_id)
        print "%s: %s" % ("id:"+address.id, "name:"+address.address)
                 
    def getTransactionsForAddress(self, acc_id, add_id):
        transactions = self.client.get_address_transactions(acc_id, add_id)
        for transaction in transactions.data:
            amount = transaction.amount +" "+ transaction.currency
            print "ID: %s" % (transaction.id)
            print "Type: %s" % (transaction.type)
            print "Status: %s" % (transaction.status)
            print "Amount: %s" % (amount.amount)
        print "No habia nada"
        
    def get_transactionsForAccount(self, acc_id):
        return self.client.get_transactions(acc_id)

    def transferMoneyBetweenAccount(self, acc_id, dest, myamount, mycurrency):
        transaction = self.client.transfer_money(acc_id, to=dest, amount=myamount, currency=mycurrency)            
     
    def transferMoneyBetweenAccount(self, acc_id, dest, myamount, mycurrency):
        transaction = self.client.transfer_money(acc_id, to=dest, amount=myamount, currency=mycurrency)

        #Check a method to get last transaction or transaction by id instead.
        amount = transaction.amount
        details = transaction.details
        print "ID: %s" % (transaction.id)
        print "Type: %s" % (transaction.type)
        print "Status: %s" % (transaction.status)
        print "Amount: %s %s" % (amount.amount, amount.currency)
        print "Title: %s" % (details.title)
              
    def transferMoneyBetweenAccount(self, acc_id, dest, myamount, mycurrency):
        transaction = self.client.transfer_money(acc_id, to=dest, amount=myamount, currency=mycurrency)
        #Check a method to get last transaction or transaction by id instead.
        amount = transaction.amount
        destination = transaction.to    
        print "ID: %s" % (transaction.id)
        print "Type: %s" % (transaction.type)
        print "Status: %s" % (transaction.status)
        print "Amount: %s %s" % (amount.amount, amount.currency)
        print "To: %s" % (destination.address)
            
    ########## myidem, unique token to avoid the same transfer to be made twice
    def sendMoney(self, acc_id, dest, myamount, mycurrency, mydesc=""):
        transaction = self.client.send_money(acc_id, to=dest, amount=myamount, currency=mycurrency, description=mydesc)
        amount = transaction.data.amount
        destination = transaction.data.to

    def get_buy_price(self, currency_pair = 'BTC-EUR'):
         return client.get_buy_price(currency_pair = 'BTC-EUR')

            
    def get_sell_price(self, currency_pair = 'BTC-EUR'):
        return client.get_sell_price(currency_pair = 'BTC-EUR')
   
    def getExchangeRates(self, base_currency='BTC'):
        rates_list = self.client.get_exchange_rates(currency=base_currency)
        return rates_list["rates"]["EUR"]        
            
    def getAllAccountsBalance(self):
        s = ("EUR", "BTC", "ETH", "LTC", "BCH")
        accounts = self.getWalletAccounts()
        dic = dict.fromkeys(s,0)
        total = 0.00
        btc_rate = self.getExchangeRates()
        eth_rate = self.getExchangeRates('ETH')
        ltc_rate = self.getExchangeRates('LTC')
        for account in accounts.data:
            balance = account.balance
            dic[account.currency]+= float(balance.amount)
            if account.currency == "EUR":
                total += float(balance.amount)
            if account.currency == "BTC":             
                total += float(btc_rate) * float(balance.amount)
            if account.currency == "ETH":
                total += float(eth_rate) * float(balance.amount)    
            if account.currency == "LTC":
                total += float(ltc_rate) * float(balance.amount)
        dic["total"] = float(total)
            
        return dic

    def getVaults(self):
        listOfVaults = []
        
        accounts = self.getWalletAccounts()
        for account in accounts.data:
            if account.type == "vault":
                listOfVaults.append(account)
        
        return listOfVaults
     
    def getBuys(self, acc_id):
        txs = self.client.get_buys(acc_id)
        return txs    
     
    def getOneBuy(self, acc_id, tx_id):
        buy = self.client.get_buy(acc_id, tx_id)
        return buy
                        
    def placeBuyOrder(self, acc_id, myAmount, myCurrency, myPaymentMethod=""):
        if myPaymentMethod == "":
            myPaymentMethod = getMainPaymentMethod().data.id
        
        """buy = self.client.buy(acc_id,
                myAmount,
                myCurrency,
                payment_method=myPaymentMethod,
                commit=True)"""

                        
    def commitBuyOrder(self, acc_id, buy_id):        
        buy = self.client.commit_buy(acc_id, buy_id)        
  
    def getPaymentMethods(self):        
        pms = self.client.get_payment_methods()      
        return pms

    def getMainPaymentMethod(self):        
        pms = self.client.get_payment_methods()
        for pm in pms.data:
            if pm.type == "fiat_account":      
                return pm

    def getSells(self, acc_id):
        txs = self.client.get_sells(acc_id)
        return txs    
        
    def getOneSell(self, acc_id, tx_id):
        sell = self.client.get_sell(acc_id, tx_id)
        return sell
         
    def placeSellOrder(self, acc_id, myAmount, myCurrency, myPaymentMethod="", myCommit=True):
        if myPaymentMethod == "":
            myPaymentMethod = getMainPaymentMethod()
        sell = self.client.sell(acc_id,
                myAmount,
                myCurrency,
                payment_method=myPaymentMethod,
                commit=myCommit)
                   
    def commitSellOrder(self, acc_id, sell_id):        
        sell = self.client.commit_sell(acc_id, sell_id)        
 
    def getDeposits(self, acc_id):
        deps = self.client.get_deposits(acc_id)
        return deps    
   
    def getOneDeposit(self, acc_id, dep_id):
        dep = self.client.get_deposit(acc_id, dep_id)
        return dep
        
    def placeDepositOrder(self, acc_id, myAmount, myCurrency, myPaymentMethod="", myCommit=True):
        if myPaymentMethod == "":
            myPaymentMethod = getMainPaymentMethod()
        dep = self.client.deposit(acc_id,
                myAmount,
                myCurrency,
                payment_method=myPaymentMethod,
                commit=myCommit)
                           
    def commitDeposit(self, acc_id, deposit_id):        
        deposit = self.client.commit_deposit(acc_id, deposit_id)        
        
   
    def getWithdrawalas(self, acc_id):
        withdrawals = self.client.get_withdrawals(acc_id)
        return withdrawals    
                 
    def getOneWithdrawal(self, acc_id, withdrawals_id):
        withdrawal = self.client.get_withdrawal(acc_id, withdrawals_id)
        return withdrawal
            
    def placeWithdrawalOrder(self, acc_id, myAmount, myCurrency, myPaymentMethod="", myCommit=True):
        if myPaymentMethod == "":
            myPaymentMethod = getMainPaymentMethod()
        withdrawal = self.client.withdraw(acc_id,
                myAmount,
                myCurrency,
                payment_method=myPaymentMethod,
                commit=myCommit)
                       
    def commitWithdrawal(self, acc_id, withdrawal_id):        
        withdrawal = self.client.commit_withdrawal(acc_id, withdrawal_id)        
        
             
        
        
        
        
        
        
        
        