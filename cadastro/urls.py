from django.urls import path

from . import views

app_name = 'cadastro'
urlpatterns = [
    path('cadastro/', views.register_user, name='register'),
    path('login_user/', views.login_user, name='login'),
    path('perfil/', views.change_password, name='change_password'),
]
