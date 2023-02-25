from django.db import models

from cadastro.models import User


class Currency(models.Model):

    class Meta:
        verbose_name = 'Moeda'

    name = models.CharField('Nome', max_length=10)
    code = models.CharField('Código', max_length=10)


class Asset(models.Model):

    class Meta:
        verbose_name = 'Ativo'

    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    name = models.CharField('Nome do ativo', max_length=50)
    description = models.CharField('Descrição', max_length=100)
    market = models.CharField('Mercado', max_length=50)
    type = models.CharField('Tipo de investimento', max_length=50)
    group = models.CharField('Grupo de investimento', max_length=50)
    expiration_date = models.DateTimeField('Vencimento', blank=True, null=True)

    def __str__(self):
        return self.name


class Wallet(models.Model):

    class Meta:
        verbose_name = 'Carteira'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField('Data')

    def __str__(self):
        return self.user.email + ' | ' + self.date.strftime('%Y-%m-%d')


class Content(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    institution = models.CharField('Instituição', max_length=50)
    quantity = models.FloatField('Quantidade')
    cost = models.FloatField('Custo')
    price = models.FloatField('Cotação')

    def __str__(self):
        return self.asset.name + ' | ' + self.institution


class MarketAgg(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    market = models.CharField('Mercado', max_length=50)
    cost = models.FloatField('Custo')
    value = models.FloatField('Valor')

    def __str__(self):
        return str(self.user) + ' | ' + self.wallet.date.strftime('%Y-%m-%d')
