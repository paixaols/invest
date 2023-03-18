from django.urls import path

from . import views

app_name = 'invest'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('investimentos/', views.ContentListView.as_view(), name='wallet'),
    path('investimentos/detail/<int:content_id>/', views.ContentDetail.as_view(), name='content_detail')
]
