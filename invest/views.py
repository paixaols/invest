import pandas as pd

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from .models import Asset, Content, Market, MarketAgg, Wallet
from cadastro.models import User


def qs_to_df(queryset):
    q = queryset.values()
    df = pd.DataFrame.from_records(q)
    return df


def market_aggregation(request, wallet_id):
    try:
        wallet = Wallet.objects.get(pk=wallet_id)
    except:
        return HttpResponse(status=200)

    # Conteúdo da carteira
    df_content = qs_to_df(
        Content.objects.filter(wallet_id=wallet_id)
    )
    df_content['value'] = df_content['quantity'] * df_content['price']

    # Associar info dos ativos
    asset_ids = df_content['asset_id'].unique()
    df_assets = qs_to_df(
        Asset.objects.filter(pk__in=asset_ids)
    )
    df_content = df_content.merge(
        df_assets, how='left', left_on='asset_id', right_on='id',
        suffixes=('', '_asset')
    )

    # Agregar valores
    market_agg = df_content[['market_id', 'cost', 'value']].groupby('market_id').sum().reset_index()

    # Inserir ou atualizar BD
    market_agg['defaults'] = market_agg.apply(lambda x: x.to_dict(), axis=1)
    market_agg['update_create'] = market_agg.apply(
        lambda x: MarketAgg.objects.update_or_create(
            user_id=wallet.user.id,
            wallet_id=wallet_id,
            market_id=x['market_id'],
            defaults=x['defaults']
        ),
        axis=1
    )

    return HttpResponse(status=200)


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
        market_agg = MarketAgg.objects.filter(wallet_id=wallet.id)
        context = {
            # 'last_updated': wallet.date,
            'last_updated': wallet.date.strftime('%d/%m/%Y'),
            'market_agg_table': market_agg
        }

        return render(request, 'invest/home.html', context)
