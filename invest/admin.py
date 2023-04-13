from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Asset, Bank, Content, AssetGroup, AssetType, Market, Wallet
)
from cadastro.models import User
from statement.models import Dividend, Transaction

MAX_ENTRIES_PER_PAGE = 15


# ---------------------------------------------------------------------------- #
# Cadastro
# ---------------------------------------------------------------------------- #
class UserProfileAdmin(UserAdmin):
    # Customize the list page.
    search_fields = ['email', 'first_name', 'last_name']
    list_display = [
        'email', 'first_name', 'last_name', 'is_active', 'is_staff',
        'is_superuser', 'date_joined', 'last_login'
    ]
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    list_per_page = MAX_ENTRIES_PER_PAGE

    # Customize the detail form page.
    fieldsets = [
        ('Informações pessoais', {'fields': [
            'first_name', 'last_name', 'email', 'username', 'password'
        ]}),
        ('Permissões', {'fields': [
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
        ]}),
        ('Datas importantes', {'fields': ['date_joined', 'last_login']}),
    ]

admin.site.register(User, UserProfileAdmin)


# ---------------------------------------------------------------------------- #
# Invest
# ---------------------------------------------------------------------------- #
class AssetAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']
    list_display = [
        'name', 'description', 'market', 'type', 'group', 'expiration_date'
    ]
    list_filter = ['market', 'type', 'group']
    list_per_page = MAX_ENTRIES_PER_PAGE

admin.site.register(Asset, AssetAdmin)


class BankAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']
    list_display = [
        'name', 'market'
    ]
    list_filter = ['market']
    list_per_page = MAX_ENTRIES_PER_PAGE

admin.site.register(Bank, BankAdmin)


class ContentInline(admin.TabularInline):
    model = Content
    extra = 0


class WalletAdmin(admin.ModelAdmin):
    search_fields = ['user__email']
    list_display = [
        'user', 'dt_created', 'dt_updated'
    ]
    list_per_page = MAX_ENTRIES_PER_PAGE
    inlines = [ContentInline]

admin.site.register(Wallet, WalletAdmin)


class GroupAdmin(admin.ModelAdmin):
    search_fields = ['group']
    list_display = [
        'group'
    ]
    list_per_page = MAX_ENTRIES_PER_PAGE

admin.site.register(AssetGroup, GroupAdmin)

admin.site.register(Market)
admin.site.register(AssetType)


# ---------------------------------------------------------------------------- #
# Statement
# ---------------------------------------------------------------------------- #
class DividendAdmin(admin.ModelAdmin):
    search_fields = ['asset__name', 'bank__name']
    list_display = [
        'date', 'asset', 'bank', 'value', 'asset_currency'
    ]
    list_per_page = MAX_ENTRIES_PER_PAGE

    @admin.display(ordering='asset__market__currency', description='Moeda')
    def asset_currency(self, obj):
        return obj.asset.market.currency

    def get_queryset(self, request):
        return Dividend.objects.filter(user=request.user)

admin.site.register(Dividend, DividendAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'event', 'asset', 'quantity', 'bank'
    ]
    list_filter = ['event', 'bank']
    list_per_page = MAX_ENTRIES_PER_PAGE

    def get_queryset(self, request):
        return Transaction.objects.filter(user=request.user)

admin.site.register(Transaction, TransactionAdmin)
