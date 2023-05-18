from django.urls import path

from . import views

app_name = 'api'
urlpatterns = [
    path('get-assets/', views.get_assets, name='get_assets'),
    path('get-asset-groups/', views.get_asset_groups, name='get_asset_groups'),
    path('get-asset-types/', views.get_asset_types, name='get_asset_types'),
    path('get-markets/', views.get_markets, name='get_markets'),
    path('price-history/<str:code>/', views.price_history, name='price_history'),
]
