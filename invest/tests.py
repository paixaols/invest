from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Asset, AssetGroup, AssetType, Bank, Content, GroupAgg, Market, MarketAgg,
    Wallet
)
from cadastro.models import User
from statement.models import Transaction


# ---------------------------------------------------------------------------- #
# Test models
# ---------------------------------------------------------------------------- #
class ContentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@dev.com', password='123')
        self.asset_type = AssetType.objects.create(type='Test Type')
        self.asset_group = AssetGroup.objects.create(group='Test Group')
        self.market = Market.objects.create(name='Test Market')
        self.asset = Asset.objects.create(
            name='TEST', type=self.asset_type, group=self.asset_group, market=self.market
        )
        self.wallet = Wallet.objects.create(user=self.user, dt_created=timezone.now())
        self.bank = Bank.objects.create(name='Banco da Esquina', market=self.market)

    def test_save_method_on_content_creation(self):
        '''O método save do modelo Content deve calcular o valor.'''
        c = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset, bank=self.bank,
            quantity=2, price=3, cost=3, dt_updated=self.wallet.dt_created
        )
        self.assertEqual(c.quantity, 2)
        self.assertEqual(c.price, 3)
        self.assertEqual(c.value, 6)

    def test_save_method_on_content_update(self):
        '''O método save do modelo Content deve calcular o valor.'''
        c = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset, bank=self.bank,
            quantity=2, price=3, cost=3, dt_updated=self.wallet.dt_created
        )
        self.assertEqual(c.quantity, 2)
        self.assertEqual(c.price, 3)
        self.assertEqual(c.value, 6)

        # Change instance
        c.quantity = 3
        self.assertEqual(c.quantity, 3)
        self.assertEqual(c.price, 3)
        self.assertEqual(c.value, 6)

        # Save changes
        c.save(update_fields=['quantity'])
        self.assertEqual(c.value, 9)


# ---------------------------------------------------------------------------- #
# Test signals
# ---------------------------------------------------------------------------- #
class ContentAggregationSignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@dev.com', password='123')
        self.asset_type = AssetType.objects.create(type='Test Type')
        self.market_a = Market.objects.create(name='Market A')
        self.market_b = Market.objects.create(name='Market B')
        self.group_x = AssetGroup.objects.create(group='Group X')
        self.group_y = AssetGroup.objects.create(group='Group Y')
        self.asset_1 = Asset.objects.create(
            name='Asset market A', type=self.asset_type, group=self.group_x, market=self.market_a
        )
        self.asset_2 = Asset.objects.create(
            name='Asset market B', type=self.asset_type, group=self.group_x, market=self.market_b
        )
        self.asset_3 = Asset.objects.create(
            name='Asset group X', type=self.asset_type, group=self.group_x, market=self.market_a
        )
        self.asset_4 = Asset.objects.create(
            name='Asset group Y', type=self.asset_type, group=self.group_y, market=self.market_a
        )
        self.wallet = Wallet.objects.create(user=self.user, dt_created=timezone.now())
        self.bank_a = Bank.objects.create(name='Banco da Esquina', market=self.market_a)
        self.bank_b = Bank.objects.create(name='Banco da Esquina', market=self.market_b)

    def test_market_aggregation_on_content_post_save(self):
        agg_exists = MarketAgg.objects.filter(wallet=self.wallet).exists()
        self.assertIs(agg_exists, False)

        c = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset_1, bank=self.bank_a,
            quantity=2, price=3, cost=3, dt_updated=self.wallet.dt_created
        )

        agg_exists = MarketAgg.objects.filter(wallet=self.wallet).exists()
        self.assertIs(agg_exists, True)

    def test_market_aggregation_on_content_post_delete(self):
        agg_exists = MarketAgg.objects.filter(wallet=self.wallet).exists()
        self.assertIs(agg_exists, False)

        c1 = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset_1, bank=self.bank_a,
            quantity=2, price=3, cost=3, dt_updated=self.wallet.dt_created
        )
        c2 = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset_2, bank=self.bank_b,
            quantity=2, price=3, cost=3, dt_updated=self.wallet.dt_created
        )

        agg = MarketAgg.objects.filter(wallet=self.wallet)
        self.assertEqual(len(agg), 2)

        c1.delete()
        agg = MarketAgg.objects.filter(wallet=self.wallet)
        self.assertEqual(len(agg), 1)

        c2.delete()
        agg_exists = MarketAgg.objects.filter(wallet=self.wallet).exists()
        self.assertEqual(agg_exists, False)

    def test_group_aggregation_on_content_post_save(self):
        agg_exists = GroupAgg.objects.filter(wallet=self.wallet).exists()
        self.assertIs(agg_exists, False)

        c = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset_3, bank=self.bank_a,
            quantity=2, price=3, cost=3, dt_updated=self.wallet.dt_created
        )

        agg_exists = GroupAgg.objects.filter(wallet=self.wallet).exists()
        self.assertIs(agg_exists, True)

    def test_group_aggregation_on_content_post_delete(self):
        agg_exists = GroupAgg.objects.filter(wallet=self.wallet).exists()
        self.assertIs(agg_exists, False)

        c1 = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset_3, bank=self.bank_a,
            quantity=2, price=3, cost=3, dt_updated=self.wallet.dt_created
        )
        c2 = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset_4, bank=self.bank_b,
            quantity=2, price=3, cost=3, dt_updated=self.wallet.dt_created
        )

        agg = GroupAgg.objects.filter(wallet=self.wallet)
        self.assertEqual(len(agg), 2)

        c1.delete()
        agg = GroupAgg.objects.filter(wallet=self.wallet)
        self.assertEqual(len(agg), 1)

        c2.delete()
        agg_exists = GroupAgg.objects.filter(wallet=self.wallet).exists()
        self.assertEqual(agg_exists, False)


# ---------------------------------------------------------------------------- #
# Test views
# ---------------------------------------------------------------------------- #
class UpdateWalletViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@dev.com', password='123')
        self.asset_type = AssetType.objects.create(type='Test Type')
        self.asset_group = AssetGroup.objects.create(group='Test Group')
        self.market = Market.objects.create(name='Test Market')
        self.bank = Bank.objects.create(name='Bank', market=self.market)
        self.asset1 = Asset.objects.create(
            name='TEST 1', type=self.asset_type, group=self.asset_group, market=self.market
        )
        self.asset2 = Asset.objects.create(
            name='TEST 2', type=self.asset_type, group=self.asset_group, market=self.market
        )

        self.t_rv = AssetType.objects.create(type='Renda Variável')
        self.g_acao = AssetGroup.objects.create(group='Ação')
        self.g_etf = AssetGroup.objects.create(group='ETF')
        self.m_brasil = Market.objects.create(name='Brasil', yf_suffix='.SA')
        self.m_eua = Market.objects.create(name='EUA')
        self.bbas3 = Asset.objects.create(
            name='BBAS3', type=self.t_rv, group=self.g_acao, market=self.m_brasil
        )
        self.ivv = Asset.objects.create(
            name='IVV', type=self.t_rv, group=self.g_etf, market=self.m_eua
        )

        self.client = Client()
        self.client.force_login(self.user)

    def test_consolidate_first_wallet(self):
        Transaction.objects.create(
            user=self.user, asset=self.asset1, bank = self.bank,
            date = timezone.now(), event = 'COMPRA',
            quantity = 1, value = 10, fee = 0,
            currency_rate = 1,
            pre_split = 1, post_split = 1
        )

        self.assertIs(Wallet.objects.all().exists(), False)
        response = self.client.get(reverse('invest:update_wallet'))
        self.assertRedirects(response, reverse('invest:home'))
        self.assertEqual(len(Wallet.objects.all()), 1)

    def test_update_existing_wallet(self):
        # Buy asset 1
        Transaction.objects.create(
            user=self.user, asset=self.asset1, bank = self.bank,
            date = timezone.now(), event = 'COMPRA',
            quantity = 1, value = 10, fee = 0,
            currency_rate = 1,
            pre_split = 1, post_split = 1
        )

        self.assertIs(Wallet.objects.all().exists(), False)
        response = self.client.get(reverse('invest:update_wallet'))
        self.assertRedirects(response, reverse('invest:home'))

        wallet = Wallet.objects.filter(user=self.user).latest('dt_created')
        contents = Content.objects.filter(wallet=wallet)
        self.assertEqual(contents[0].quantity, 1)

        # More asset 1
        Transaction.objects.create(
            user=self.user, asset=self.asset1, bank = self.bank,
            date = timezone.now(), event = 'COMPRA',
            quantity = 1, value = 10, fee = 0,
            currency_rate = 1,
            pre_split = 1, post_split = 1
        )

        response = self.client.get(reverse('invest:update_wallet'))
        self.assertRedirects(response, reverse('invest:home'))

        wallet = Wallet.objects.filter(user=self.user).latest('dt_created')
        contents = Content.objects.filter(wallet=wallet)
        self.assertEqual(contents[0].quantity, 2)

        # Buy asset 2
        Transaction.objects.create(
            user=self.user, asset=self.asset2, bank = self.bank,
            date = timezone.now(), event = 'COMPRA',
            quantity = 5, value = 50, fee = 1,
            currency_rate = 1,
            pre_split = 1, post_split = 1
        )

        response = self.client.get(reverse('invest:update_wallet'))
        self.assertRedirects(response, reverse('invest:home'))

        wallet = Wallet.objects.filter(user=self.user).latest('dt_created')
        contents = Content.objects.filter(wallet=wallet)
        self.assertEqual(len(contents), 2)
        content = Content.objects.get(wallet=wallet, asset__name='TEST 2')
        self.assertEqual(content.quantity, 5)

        # Sell asset 1
        Transaction.objects.create(
            user=self.user, asset=self.asset1, bank = self.bank,
            date = timezone.now(), event = 'VENDA',
            quantity = 2, value = 20, fee = 0,
            currency_rate = 1,
            pre_split = 1, post_split = 1
        )

        response = self.client.get(reverse('invest:update_wallet'))
        self.assertRedirects(response, reverse('invest:home'))

        wallet = Wallet.objects.filter(user=self.user).latest('dt_created')
        contents = Content.objects.filter(wallet=wallet)
        self.assertEqual(len(contents), 1)
        self.assertEqual(contents[0].asset.name, 'TEST 2')

    def test_event_compra(self):
        Transaction.objects.create(
            user=self.user, asset=self.asset1, bank = self.bank,
            date = timezone.now(), event = 'COMPRA',
            quantity = 1, value = 10, fee = 0,
            currency_rate = 1,
            pre_split = 1, post_split = 1
        )
        Transaction.objects.create(
            user=self.user, asset=self.asset2, bank = self.bank,
            date = timezone.now(), event = 'COMPRA',
            quantity = 2, value = 20, fee = 2,
            currency_rate = 1,
            pre_split = 1, post_split = 1
        )

        response = self.client.get(reverse('invest:update_wallet'))
        self.assertRedirects(response, reverse('invest:home'))

        wallet = Wallet.objects.filter(user=self.user).latest('dt_created')
        contents = Content.objects.filter(wallet=wallet)
        self.assertEqual(len(contents), 2)
