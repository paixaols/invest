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
from .models import Content, GroupAgg, Market, MarketAgg, Wallet
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

        # Evolução patrimonial
        markets = Market.objects.all()
        wallets = Wallet.objects.filter(user=request.user)

        agg = MarketAgg.objects.filter(user=request.user)
        df = qs_to_df(agg)
        df_value = df.pivot(index='wallet_id',values='value',columns='market_id').reset_index()
        df_value.fillna(0, inplace=True)
        df_value['date'] = df_value['wallet_id'].apply(lambda x: wallets.get(pk=x).dt_updated.strftime('%Y-%m-%d'))

        df['gain'] = df['value']-df['cost']
        df_gain = df.pivot(index='wallet_id', values='gain', columns='market_id').reset_index()
        df_gain.fillna(0, inplace=True)
        df_gain['date'] = df_gain['wallet_id'].apply(lambda x: wallets.get(pk=x).dt_updated.strftime('%Y-%m-%d'))

        history_plot = {
            'date': df_value['date'].to_list(),
            'datasets': []
        }
        gain_plot = {
            'date': df_value['date'].to_list(),
            'datasets': []
        }
        for mkt_id in df['market_id'].unique():
            market = markets.get(pk=mkt_id).name
            currency = markets.get(pk=mkt_id).symbol
            history_plot['datasets'].append({
                'data': df_value[mkt_id].to_list(),
                'label': currency
            })
            gain_plot['datasets'].append({
                'data': df_gain[mkt_id].to_list(),
                'label': currency
            })

        context = {
            'last_updated': wallet.dt_updated,
            'market_agg_table': market_agg,
            'group_agg': group_agg,
            'group_plot': json.dumps(group_plot),
            'history_plot': json.dumps(history_plot),
            'gain_plot': json.dumps(gain_plot)
        }

        return render(request, 'invest/home/home.html', context)


class UpdateWalletView(LoginRequiredMixin, View):
    login_url = 'cadastro:login'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        user = request.user

        # Consolidate statement
        w, transactions = self.consolidate_transaction_statement(user)

        # Update or create wallet
        current_wallet, previous_wallet_id = self.update_wallet(user)
        if current_wallet is not None:# Update existing wallet for the current month
            for k in w.keys():
                asset_id, bank_id = k.split(':')
                asset_id = int(asset_id)
                bank_id = int(bank_id)
                Content.objects.update_or_create(
                    wallet=current_wallet,
                    user=user,
                    asset_id=asset_id,
                    bank_id=bank_id,
                    defaults={
                        'quantity': w.get(k).get('quantity'),
                        'cost': w.get(k).get('cost'),
                        'price': 0,
                        'dt_updated': current_wallet.dt_created
                    }
                )
            current_wallet.save()# Update field dt_updated

            # Remove assets sold since last update
            Content.objects.filter(wallet=current_wallet, quantity=0).delete()

        else:# Create new wallet
            new_wallet = Wallet.objects.create(user=user, dt_created=timezone.now())
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
            # TODO: não deveria ser removido no método consolidate_transaction_statement? Criar testes incluindo venda
            Content.objects.filter(wallet=new_wallet, quantity=0).delete()

            # Copiar caixa da carteira anterior
            if previous_wallet_id is not None:
                contents_in_statement = [ f'{t.asset_id}:{t.bank_id}' for t in transactions ]
                contents = Content.objects.filter(wallet_id=previous_wallet_id)
                contents_in_last_wallet = [ f'{c.asset_id}:{c.bank_id}' for c in contents ]
                transfer_content = [ c for c in contents_in_last_wallet if c not in contents_in_statement ]
                for c in transfer_content:
                    asset_id, bank_id = c.split(':')
                    asset_id = int(asset_id)
                    bank_id = int(bank_id)
                    content = contents.get(asset_id=asset_id, bank_id=bank_id)# Asset e bank definem um content unicamente dentro de uma carteira.
                    Content.objects.create(
                        wallet=new_wallet,
                        user=user,
                        asset_id=asset_id,
                        bank_id=bank_id,
                        quantity=content.quantity,
                        cost=content.cost,
                        price=content.price,
                        dt_updated=new_wallet.dt_created
                    )

        return HttpResponseRedirect(reverse('invest:home'))

    def update_wallet(self, user):
        '''
        Returns the wallet to be updated (current month), otherwise none.
        Returns the id of the previous wallet, whatever month it was created (to copy assets inserted manually).
        '''
        qs = Wallet.objects.filter(user=user).order_by('-dt_created')[:1]
        now = timezone.now()
        previous_wallet_id = None
        if qs.exists():
            wallet = qs[0]
            previous_wallet_id = wallet.id
            if wallet.dt_created.month == now.month:# Update existing wallet
                create_new_wallet = False
                return wallet, None
        return None, previous_wallet_id

    def consolidate_transaction_statement(self, user):
        # Key -> asset.id:bank.id
        # {
        #     '1:1': {'quantity': 1.0, 'cost': 10.0},
        #     '2:1': {'quantity': 2.0, 'cost': 22.0}
        # }
        transactions = Transaction.objects.filter(user=user)
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
        return w, transactions


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
        contents2update = Content.objects.filter(user=user, wallet=wallet)

        # Yahoo Finance
        contents = contents2update.filter(asset__source='YF')
        contents2update = contents2update.exclude(asset__source='YF')

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
            # content.dt_updated = date
            content.save()

        # Além do YF
        qs = Wallet.objects.filter(user=user, dt_created__lt=wallet.dt_created)
        if qs.exists():# Copy values from previous wallet
            previous_wallet = qs.latest('dt_created')
            for content in contents2update:
                asset = content.asset
                bank = content.bank
                pcont = Content.objects.filter(
                    wallet=previous_wallet,
                    asset=asset,
                    bank=bank
                )
                if pcont.exists():# Conteúdo já existia na carteira anterior
                    content.price = pcont[0].price
                else:# Ou é novo nessa carteira
                    content.price = content.cost/content.quantity
                content.save()
        else:# Copy cost from current wallet
            for content in contents2update:
                content.price = content.cost/content.quantity
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
