from django.db import models
from django.utils import timezone

from cadastro.models import User


class Market(models.Model):

    class Meta:
        verbose_name = 'Local'
        verbose_name_plural = 'Locais'

    name = models.CharField('Local', max_length=50)
    currency = models.CharField('Moeda', max_length=10)
    code = models.CharField('Código', max_length=10)
    symbol = models.CharField('Símbolo', max_length=10)
    yf_suffix = models.CharField('Sufixo Yahoo Finance', max_length=5, blank=True, null=True)

    def __str__(self):
        return self.name


class Bank(models.Model):

    class Meta:
        verbose_name = 'Banco'

    name = models.CharField('Nome do banco ou corretora', max_length=50)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class AssetType(models.Model):

    class Meta:
        verbose_name = 'Tipo de Investimento'
        verbose_name_plural = 'Tipos de Investimento'

    type = models.CharField('Tipo', max_length=50)

    def __str__(self):
        return self.type


class AssetGroup(models.Model):

    class Meta:
        verbose_name = 'Grupo de Investimento'
        verbose_name_plural = 'Grupos de Investimento'

    group = models.CharField('Grupo', max_length=50)

    def __str__(self):
        return self.group


class Asset(models.Model):

    SOURCE_CHOICES = [('MANUAL', 'Manual'), ('YF', 'Yahoo Finance')]

    class Meta:
        verbose_name = 'Ativo'

    name = models.CharField('Nome do ativo', max_length=50)
    description = models.CharField('Descrição', max_length=100)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    type = models.ForeignKey(AssetType, on_delete=models.CASCADE)
    group = models.ForeignKey(AssetGroup, on_delete=models.CASCADE)
    expiration_date = models.DateTimeField('Vencimento', blank=True, null=True)
    source = models.CharField(
        'Fonte',
        max_length=10,
        choices=SOURCE_CHOICES
    )

    def __str__(self):
        if self.expiration_date is None:
            return self.name
        else:
            return self.name + ' | ' + self.expiration_date.strftime('%Y-%m-%d')


class Wallet(models.Model):

    class Meta:
        verbose_name = 'Carteira'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dt_created = models.DateTimeField('Data de criação')
    dt_updated = models.DateTimeField('Data de atualização')

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.dt_updated = timezone.now()
        if update_fields is not None:
            update_fields = {'dt_updated'}.union(update_fields)

        super().save(
            force_insert=force_insert, force_update=force_update, using=using,
            update_fields=update_fields
        )

    def __str__(self):
        return self.user.email + ' | ' + self.dt_updated.strftime('%Y-%m-%d %H:%M:%S %Z')


class Content(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    quantity = models.FloatField('Quantidade')
    cost = models.FloatField('Custo')
    price = models.FloatField('Cotação')
    value = models.FloatField('Valor')
    dt_updated = models.DateField('Data de atualização')

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.value = self.quantity*self.price
        self.dt_updated = timezone.now()
        if update_fields is not None:
            update_fields = {'dt_updated'}.union(update_fields)
            if 'quantity' in update_fields or 'price' in update_fields:
                update_fields = {'value'}.union(update_fields)

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def __str__(self):
        return self.asset.name + ' | ' + self.bank.name


class MarketAgg(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    cost = models.FloatField('Custo')
    value = models.FloatField('Valor')

    def __str__(self):
        return str(self.user) + ' | ' + str(self.market) + ' | ' + self.wallet.dt_updated.strftime('%Y-%m-%d')


class GroupAgg(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    group = models.ForeignKey(AssetGroup, on_delete=models.CASCADE)
    cost = models.FloatField('Custo')
    value = models.FloatField('Valor')

    def __str__(self):
        return str(self.user) + ' | ' + str(self.group) + ' | ' + self.wallet.dt_updated.strftime('%Y-%m-%d')
