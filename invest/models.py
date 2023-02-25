from django.db import models

from cadastro.models import User


class Currency(models.Model):

    class Meta:
        verbose_name = 'Moeda'

    currency = models.CharField('Nome', max_length=10)
    code = models.CharField('Código', max_length=10)

    def __str__(self):
        return self.currency


class Market(models.Model):

    class Meta:
        verbose_name = 'Local'
        verbose_name_plural = 'Locais'

    market = models.CharField('Local', max_length=50)

    def __str__(self):
        return self.market


class InvestType(models.Model):

    class Meta:
        verbose_name = 'Tipo de Investimento'
        verbose_name_plural = 'Tipos de Investimento'

    type = models.CharField('Tipo', max_length=50)

    def __str__(self):
        return self.type


class InvestGroup(models.Model):

    class Meta:
        verbose_name = 'Grupo de Investimento'
        verbose_name_plural = 'Grupos de Investimento'

    group = models.CharField('Grupo', max_length=50)

    def __str__(self):
        return self.group


class Asset(models.Model):

    class Meta:
        verbose_name = 'Ativo'

    name = models.CharField('Nome do ativo', max_length=50)
    description = models.CharField('Descrição', max_length=100)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    type = models.ForeignKey(InvestType, on_delete=models.CASCADE)
    group = models.ForeignKey(InvestGroup, on_delete=models.CASCADE)
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
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    cost = models.FloatField('Custo')
    value = models.FloatField('Valor')

    def __str__(self):
        return str(self.user) + ' | ' + self.wallet.date.strftime('%Y-%m-%d')
