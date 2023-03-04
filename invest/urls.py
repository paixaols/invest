from django.urls import path

from . import views

app_name = 'invest'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('home/', views.HomeView.as_view(), name='home'),
    # path('agg/<int:wallet_id>', views.aggregation, name='magg'),
    # path('wallet/', views.CurrentWalletView.as_view(), name='wallet'),
]
