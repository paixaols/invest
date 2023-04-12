from django.db import models

from cadastro.models import User
from invest.models import Asset, Bank, Wallet


class Transaction(models.Model):

    EVENT_CHOICES = [('AMORTIZACAO', 'Amortização'), ('BONIFICACAO', 'Bonificação'), ('COMPRA', 'Compra'), ('DESDOBRAMENTO', 'Desdobramento'), ('GRUPAMENTO', 'Grupamento'), ('SUBSCRICAO', 'Subscrição'), ('VENDA', 'Venda')]

    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    date = models.DateTimeField('Data')
    event = models.CharField(
        'Evento',
        max_length=15,
        choices=EVENT_CHOICES
    )
    quantity = models.FloatField('Quant. negociada')
    value = models.FloatField('Valor da operação')
    fee = models.FloatField('Taxas')
    currency_rate = models.FloatField('Câmbio (para BRL)')
    pre_split = models.IntegerField('Pre split')
    post_split = models.IntegerField('Pós split')

    def __str__(self):
        return self.event + ' | ' + self.asset.name + ' | ' + self.date.strftime('%Y-%m-%d')


class Dividend(models.Model):

    class Meta:
        verbose_name = 'Dividendo'
        verbose_name_plural = 'Dividendos'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    date = models.DateField('Data do pagamento')
    value = models.FloatField('Valor recebido')

    def __str__(self):
        return self.asset.name + ' | ' + self.date.strftime('%Y-%m-%d')
