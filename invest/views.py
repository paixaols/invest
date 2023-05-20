import json
import pandas as pd

from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import View

from .forms import ContentDetailForm, NewContentForm
from .models import Content, GroupAgg, MarketAgg, Wallet
from .utils import qs_to_df
from cadastro.models import User
from statement.models import Dividend, Transaction


class IndexView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        return render(request, 'invest/index.html', {})


class HomeView(LoginRequiredMixin, View):
    login_url = 'cadastro:login'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        try:
            wallet = Wallet.objects.filter(user_id=request.user).latest('dt_updated')
        except Wallet.DoesNotExist:
            return render(request, 'invest/home/home.html', {})

        market_agg = MarketAgg.objects.filter(wallet_id=wallet.id).order_by('-value')
        markets = [ agg.market for agg in market_agg ]

        group_agg = {}
        group_plot = {}
        for market in markets:
            qs = GroupAgg.objects.filter(wallet_id=wallet.id,
                                         market=market).order_by('-value')
            df = qs_to_df(qs, 'group_id__group', 'value', 'market_id__symbol')
            df.columns = ['group', 'value', 'currency_repr']
            total = df['value'].sum()
            df['pct'] = df['value'].apply(lambda x: 100*x/total)
            group_agg[market] = df.to_dict(orient='records')
            group_plot[market.name] = {
                'x': df['group'].to_list(),
                'y': df['value'].to_list(),
                'currency_symbol': market.symbol
            }

        context = {
            'last_updated': wallet.dt_updated,
            'market_agg_table': market_agg,
            'group_agg': group_agg,
            'group_plot': json.dumps(group_plot)
        }

        return render(request, 'invest/home/home.html', context)


class ContentListView(LoginRequiredMixin, View):
    login_url = 'cadastro:login'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        try:
            wallet = Wallet.objects.filter(user_id=request.user).latest('dt_updated')
        except Wallet.DoesNotExist:
            # TODO: Mudar esse comportamento
            return render(request, 'invest/home/home.html', {})

        contents = Content.objects.filter(wallet_id=wallet.id).order_by('-value')
        markets = sorted(
            { (item.asset.market.id, item.asset.market.name) for item in contents },
            key=lambda x: x[1]
        )
        types = sorted(
            { (item.asset.type.id, item.asset.type.type) for item in contents },
            key=lambda x: x[1]
        )
        groups = sorted(
            { (item.asset.group.id, item.asset.group.group) for item in contents },
            key=lambda x: x[1]
        )

        context = {
            'date': wallet.dt_updated,
            'number_of_assets': len(contents),
            'markets': markets,
            'types': types,
            'groups': groups,
            'wallet_contents': contents,
            'new_content_form': NewContentForm()
        }
        return render(request, 'invest/wallet_content_list.html', context)


class ContentDetailView(LoginRequiredMixin, View):
    login_url = 'cadastro:login'
    http_method_names = ['get']

    def get(self, request, content_id, *args, **kwargs):
        content = get_object_or_404(Content, pk=content_id)
        if request.user != content.user:
            return HttpResponseRedirect(reverse('invest:content_list'))

        content.cm = content.cost/content.quantity
        content.value = content.quantity*content.price

        content_history = Content.objects.filter(
            user=request.user,
            asset=content.asset,
            bank=content.bank
        )
        value_history_json = serializers.serialize(
            'json',
            content_history.order_by('dt_updated'),
            fields=('dt_updated', 'value')
        )

        dividend = Dividend.objects.filter(
            user=request.user,
            asset=content.asset,
            bank=content.bank
        ).order_by('-date')
        dividend_json = serializers.serialize(
            'json',
            dividend.order_by('date'),
            fields=('date', 'value')
        )

        context = {
            'content': content,
            'asset_name': content.asset.name,
            'description': content.asset.description,
            'currency_symbol': content.asset.market.symbol,
            'value_history_json': value_history_json,
            'dividend': dividend,
            'dividend_json': dividend_json
        }

        return render(request, 'invest/content_detail.html', context)


class DeleteContentDetailView(LoginRequiredMixin, View):
    login_url = 'cadastro:login'
    http_method_names = ['get']

    def get(self, request, content_id, *args, **kwargs):
        content = get_object_or_404(Content, pk=content_id)
        if request.user == content.user:
            content.delete()
        return HttpResponseRedirect(reverse('invest:content_list'))
