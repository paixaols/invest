import json
import pandas as pd
import yfinance as yf

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


def consolidate(transactions):
    # Key -> asset.id:bank.id
    # {
    #     '1:1': {'quantity': 1.0, 'cost': 10.0},
    #     '2:1': {'quantity': 2.0, 'cost': 22.0}
    # }
    transactions = transactions.order_by('date')
    w = {}
    for t in transactions:
        content_key = f'{t.asset.id}:{t.bank.id}'
        if t.event == 'COMPRA' or t.event == 'SUBSCRICAO':
            cost = t.value + t.fee
            if content_key in w:
                w[content_key]['quantity'] += t.quantity
                w[content_key]['cost'] += cost
            else:
                w[content_key] = {
                    'quantity': t.quantity,
                    'cost': cost
                }
        elif t.event == 'VENDA':
            avg_cost = w[content_key]['cost']/w[content_key]['quantity']
            value_sold = round(avg_cost * t.quantity, 2)
            w[content_key]['cost'] -= value_sold
            w[content_key]['quantity'] -= t.quantity
        elif t.event == 'DESDOBRAMENTO':
            w[content_key]['quantity'] *= t.post_split/t.pre_split
        elif t.event == 'GRUPAMENTO':
            w[content_key]['quantity'] = round(w[content_key]['quantity']*t.post_split/t.pre_split, 5)
        elif t.event == 'BONIFICACAO':
            cost = t.value + t.fee
            w[content_key]['quantity'] += t.quantity
            w[content_key]['cost'] += cost
        elif t.event == 'AMORTIZACAO':
            w[content_key]['cost'] -= t.value
        else:
            print(f'Evento de {t.asset} não suportado em {t.date.strftime("%Y-%m-%d")}: {t.event}')
    return w


class UpdateWalletView(LoginRequiredMixin, View):
    login_url = 'cadastro:login'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        user = request.user

        # Consolidate statement
        transactions = Transaction.objects.filter(user=user)
        w = consolidate(transactions)

        # Update or create wallet
        qs = Wallet.objects.filter(user=user).order_by('-dt_created')[:1]
        now = timezone.now()
        create_new_wallet = True
        if qs.exists():
            wallet = qs[0]
            if wallet.dt_created.month == now.month:# Update existing wallet
                create_new_wallet = False
                for k in w.keys():
                    asset_id, bank_id = k.split(':')
                    asset_id = int(asset_id)
                    bank_id = int(bank_id)
                    Content.objects.update_or_create(
                        wallet=wallet,
                        user=user,
                        asset_id=asset_id,
                        bank_id=bank_id,
                        defaults={
                            'quantity': w.get(k).get('quantity'),
                            'cost': w.get(k).get('cost'),
                            'price': 0,
                            'dt_updated': wallet.dt_created
                        }
                    )
                wallet.save()# Update field dt_updated

                # Remove assets sold
                Content.objects.filter(wallet=wallet, quantity=0).delete()

        if create_new_wallet:
            new_wallet = Wallet.objects.create(user=user, dt_created=now)
            for k in w.keys():
                asset_id, bank_id = k.split(':')
                asset_id = int(asset_id)
                bank_id = int(bank_id)
                Content.objects.create(
                    wallet=new_wallet,
                    user=user,
                    asset_id=asset_id,
                    bank_id=bank_id,
                    quantity=w.get(k).get('quantity'),
                    cost=w.get(k).get('cost'),
                    price=0,
                    dt_updated=new_wallet.dt_created
                )
            # Remove assets sold
            Content.objects.filter(wallet=new_wallet, quantity=0).delete()
        return HttpResponseRedirect(reverse('invest:home'))


def YFdata(ticker_list, replace_ticker=False):
    end_date = timezone.now()
    start_date = end_date-timedelta(days=7)
    data = (
        yf.download(
            ticker_list,
            start=start_date,
            end=end_date
        )['Close']
    ).reset_index()
    if replace_ticker:
        rename = { c:c.split('.')[0] for c in data.columns }
        rename['Date'] = 'date'
    else:
        rename = {'Date':'date'}
    data.rename(columns=rename, inplace=True)

    return data


class UpdateContentValueView(LoginRequiredMixin, View):
    login_url = 'cadastro:login'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        user = request.user
        wallet = Wallet.objects.filter(user=user).latest('dt_created')
        update_contents = Content.objects.filter(user=user, wallet=wallet)

        # Yahoo Finance
        contents = update_contents.filter(asset__source='YF')

        # Obter lista de ticker no formato do Yahoo Finance
        df = qs_to_df(contents, 'asset__name', 'asset__market__yf_suffix').rename(columns={
            'asset__name': 'name', 'asset__market__yf_suffix': 'suffix'
        })
        df['ticker'] = df.apply(
            lambda x: x['name'] if x['suffix'] is None else x['name']+x['suffix'],
            axis=1
        )
        ticker_list = df['ticker'].to_list()

        # Atualizar cotação
        data = YFdata(ticker_list, replace_ticker=True)
        for content in contents:
            name = content.asset.name
            idx = data[name].last_valid_index()
            date = data.loc[idx, 'date']
            price = data.loc[idx, name]
            content.price = round(price, 2)
            content.dt_updated = date
            content.save()

        return HttpResponseRedirect(reverse('invest:home'))


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
