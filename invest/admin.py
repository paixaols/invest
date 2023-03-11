from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Asset, Content, AssetGroup, AssetType, Market, Wallet
)
from cadastro.models import User

max_entries_per_page = 15


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
    list_per_page = max_entries_per_page

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
    list_per_page = max_entries_per_page


class ContentInline(admin.TabularInline):
    model = Content
    extra = 0


class WalletAdmin(admin.ModelAdmin):
    search_fields = ['user__email']
    list_display = [
        'user', 'date'
    ]
    list_per_page = max_entries_per_page
    inlines = [ContentInline]


class GroupAdmin(admin.ModelAdmin):
    search_fields = ['group']
    list_display = [
        'group'
    ]
    list_per_page = max_entries_per_page


# Register your models here.
admin.site.register(Asset, AssetAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Market)
admin.site.register(AssetGroup, GroupAdmin)
admin.site.register(AssetType)
