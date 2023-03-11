from django import forms


class ContentDetailForm(forms.Form):
    quantity = forms.FloatField(label='Quantidade')
    cost = forms.FloatField(label='Custo')
    price = forms.FloatField(label='Cotação')
    value = forms.FloatField(label='Valor')
