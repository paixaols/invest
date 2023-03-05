import pandas as pd

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from .models import Asset, Content, GroupAgg, Market, MarketAgg, Wallet
from cadastro.models import User


def qs_to_df(queryset):
    q = queryset.values()
    df = pd.DataFrame.from_records(q)
    return df


class IndexView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        return render(request, 'invest/index.html', {})


class HomeView(LoginRequiredMixin, View):
    login_url = 'cadastro:login'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        try:
            wallet = Wallet.objects.filter(user_id=request.user).latest('date')
        except Wallet.DoesNotExist:
            return render(request, 'invest/home.html', {})

        market_agg = MarketAgg.objects.filter(wallet_id=wallet.id).order_by('-value')
        markets = [ agg.market for agg in market_agg ]

        group_agg = {}
        for market in markets:
            qs = GroupAgg.objects.filter(wallet_id=wallet.id,
                                         market=market).order_by('-value')
            group_agg[market] = qs
        context = {
            # 'last_updated': wallet.date,
            'last_updated': wallet.date.strftime('%d/%m/%Y'),
            'market_agg_table': market_agg,
            'group_agg': group_agg
        }

        return render(request, 'invest/home.html', context)


class CurrentWalletView(LoginRequiredMixin, View):
    login_url = 'cadastro:login'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        try:
            wallet = Wallet.objects.filter(user_id=request.user).latest('date')
        except Wallet.DoesNotExist:
            return render(request, 'invest/home.html', {})

        contents = Content.objects.filter(wallet_id=wallet.id)
        markets = sorted({ item.asset.market.name for item in contents })
        types = sorted({ item.asset.type.type for item in contents })
        groups = sorted({ item.asset.group.group for item in contents })

        context = {
            'date': wallet.date,
            'number_of_assets': len(contents),
            'markets': markets,
            'types': types,
            'groups': groups,
            'wallet': contents
        }
        return render(request, 'invest/current_wallet.html', context)
