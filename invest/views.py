import pandas as pd

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View

from .forms import ContentDetailForm, NewContentForm
from .models import Content, GroupAgg, MarketAgg, Wallet
from cadastro.models import User


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
            'last_updated': wallet.date.strftime('%d/%m/%Y'),
            'market_agg_table': market_agg,
            'group_agg': group_agg
        }

        return render(request, 'invest/home.html', context)


class ContentListView(LoginRequiredMixin, View):
    login_url = 'cadastro:login'
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        try:
            wallet = Wallet.objects.filter(user_id=request.user).latest('date')
        except Wallet.DoesNotExist:
            # TODO: Mudar esse comportamento
            return render(request, 'invest/home.html', {})

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
            'date': wallet.date,
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
        data = {
            'quantity': content.quantity,
            'cost': content.cost,
            'price': content.price,
            'value': content.value
        }
        context = {
            'content_id': content_id,
            'content': content,
            'asset_name': content.asset.name,
            'description': content.asset.description,
            'form': ContentDetailForm(data)
        }
        return render(request, 'invest/content_detail.html', context)


class DeleteContentDetailView(LoginRequiredMixin, View):
    login_url = 'cadastro:login'
    http_method_names = ['get']

    def get(self, request, content_id, *args, **kwargs):
        content = Content.objects.get(pk=content_id)
        content.delete()
        return HttpResponseRedirect(reverse('invest:content_list'))
