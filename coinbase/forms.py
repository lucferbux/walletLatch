from django import forms

from hashlib import sha256

digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

class AccountIdForm(forms.Form):
    account_id = forms.CharField(label='account_id', widget=forms.PasswordInput())

class CoinbaseApi(forms.Form):
    api_key = forms.CharField(label='api_key', max_length=100)
    api_secret = forms.CharField(label='api_secret', widget=forms.PasswordInput())

class TransferForm(forms.Form):
    wallet_name = forms.CharField(label='wallet_name', required=True)
    recipient = forms.CharField(label='recipient', required=True)
    amount = forms.FloatField(label='amount', required=True)
    description = forms.CharField(label='description', required=False, widget=forms.Textarea())
    
    
    def clean_recipient(self):

        rec = self.cleaned_data['recipient']
        n = 0
        length = 25
        
        for char in rec:
            n = n * 58 + digits58.index(char)
        bcbytes = ''.join(chr((n >> i*8) & 0xff) for i in reversed(range(length)))
    
        if not bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]:
            raise forms.ValidationError("Not a bitcoin address.")

        return rec

class BuyForm(forms.Form):
    CHOICES=[('Btc','Btc'),
         ('Eth','Eth'),
         ('Ltc','Ltc')]
        
    optionsRadiosInline = forms.ChoiceField(required=True,
                                            choices=CHOICES, widget=forms.RadioSelect())
    amount_main = forms.FloatField(required=True)
    amount_choosen = forms.FloatField(required=True)

class SellForm(forms.Form):
    CHOICES=[('Btc','Btc'),
         ('Eth','Eth'),
         ('Ltc','Ltc')]
        
    optionsRadiosInline = forms.ChoiceField(required=True,
                                            choices=CHOICES, widget=forms.RadioSelect())
    sell_main = forms.FloatField(required=True)
    sell_choosen = forms.FloatField(required=False)

