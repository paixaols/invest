import pandas as pd

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from .models import Asset, Content, Wallet, MarketAgg
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
    user = User.objects.get(pk=wallet.user.id)

    # Conteúdo da carteira
    df_content = qs_to_df(
        Content.objects.filter(wallet_id=wallet_id)
    )
    df_content['value'] = df_content['quantity'] * df_content['price']

    # Info dos ativos na carteira
    asset_ids = df_content['asset_id'].unique()
    df_assets = qs_to_df(
        Asset.objects.filter(pk__in=asset_ids)
    )

    # Agregar valores da carteira
    df_content = df_content.merge(
        df_assets, how='left', left_on='asset_id', right_on='id',
        suffixes=('', '_asset')
    )
    market_agg = df_content[['market', 'cost', 'value']].groupby('market').sum().reset_index()

    # Inserir ou atualizar BD
    market_agg['user'] = user
    market_agg['wallet'] = wallet
    market_agg['defaults'] = market_agg.apply(lambda x: x.to_dict(), axis=1)
    market_agg['update_create'] = market_agg.apply(
        lambda x: MarketAgg.objects.update_or_create(
            wallet_id=wallet_id,
            market=x['market'],
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
