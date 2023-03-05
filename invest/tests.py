from django.test import TestCase
from django.utils import timezone

from .models import Asset, AssetGroup, AssetType, Content, Market, Wallet
from cadastro.models import User


#--------------------------------------------------#
# Test models
#--------------------------------------------------#
def create_wallet_with_content(quantity=0, cost=0, price=0):
    '''Creates a wallet with one content.'''
    user = User.objects.create_user(email='test@dev.com', password='123')
    w = Wallet.objects.create(user=user, date=timezone.now())
    t = AssetType.objects.create(type='Test Type')
    g = AssetGroup.objects.create(group='Test Group')
    m = Market.objects.create(name='Test Market')
    asset = Asset.objects.create(name='TEST', type=t, group=g, market=m)
    c = Content.objects.create(
        wallet=w,
        user=user,
        asset=asset,
        quantity=quantity,
        price=price,
        cost=cost
    )
    return c

class ContentModelTests(TestCase):
    def test_save_method(self):
        c = create_wallet_with_content(quantity=2, price=3)
        self.assertEqual(c.quantity, 2)
        self.assertEqual(c.price, 3)
        self.assertEqual(c.value, 6)

    def test_save_method_update_fields(self):
        c = create_wallet_with_content(quantity=2, price=3)
        self.assertEqual(c.quantity, 2)
        self.assertEqual(c.price, 3)
        self.assertEqual(c.value, 6)

        c.quantity = 3
        self.assertEqual(c.quantity, 3)
        self.assertEqual(c.price, 3)
        self.assertEqual(c.value, 6)

        c.save(update_fields=['quantity'])
        self.assertEqual(c.value, 9)
