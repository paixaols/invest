from django.test import TestCase
from django.utils import timezone

from .models import (
    Asset, AssetGroup, AssetType, Content, GroupAgg, Market, MarketAgg, Wallet
)
from cadastro.models import User


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

    def test_save_method_on_content_creation(self):
        '''O método save do modelo Content deve calcular o valor.'''
        c = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset,
            quantity=2, price=3, cost=3
        )
        self.assertEqual(c.quantity, 2)
        self.assertEqual(c.price, 3)
        self.assertEqual(c.value, 6)

    def test_save_method_on_content_update(self):
        '''O método save do modelo Content deve calcular o valor.'''
        c = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset,
            quantity=2, price=3, cost=3
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

    def test_market_aggregation_on_content_post_save(self):
        agg_exists = MarketAgg.objects.filter(wallet=self.wallet).exists()
        self.assertIs(agg_exists, False)

        c = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset_1,
            quantity=2, price=3, cost=3
        )

        agg_exists = MarketAgg.objects.filter(wallet=self.wallet).exists()
        self.assertIs(agg_exists, True)

    def test_market_aggregation_on_content_post_delete(self):
        agg_exists = MarketAgg.objects.filter(wallet=self.wallet).exists()
        self.assertIs(agg_exists, False)

        c1 = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset_1,
            quantity=2, price=3, cost=3
        )
        c2 = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset_2,
            quantity=2, price=3, cost=3
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
            wallet=self.wallet, user=self.user, asset=self.asset_3,
            quantity=2, price=3, cost=3
        )

        agg_exists = GroupAgg.objects.filter(wallet=self.wallet).exists()
        self.assertIs(agg_exists, True)

    def test_group_aggregation_on_content_post_delete(self):
        agg_exists = GroupAgg.objects.filter(wallet=self.wallet).exists()
        self.assertIs(agg_exists, False)

        c1 = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset_3,
            quantity=2, price=3, cost=3
        )
        c2 = Content.objects.create(
            wallet=self.wallet, user=self.user, asset=self.asset_4,
            quantity=2, price=3, cost=3
        )

        agg = GroupAgg.objects.filter(wallet=self.wallet)
        self.assertEqual(len(agg), 2)

        c1.delete()
        agg = GroupAgg.objects.filter(wallet=self.wallet)
        self.assertEqual(len(agg), 1)

        c2.delete()
        agg_exists = GroupAgg.objects.filter(wallet=self.wallet).exists()
        self.assertEqual(agg_exists, False)
