from django.urls import path

from . import views

app_name = 'invest'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('investimentos/', views.ContentListView.as_view(), name='content_list'),
    path('investimentos/detail/<int:content_id>/', views.ContentDetailView.as_view(), name='content_detail'),
    path('investimentos/delete-content/<int:content_id>/', views.DeleteContentDetailView.as_view(), name='delete_content'),
]
