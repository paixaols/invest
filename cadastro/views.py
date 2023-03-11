from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render

from .forms import RegisterUserForm

def register_user(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso.')
            return redirect('cadastro:login')
        messages.success(request, 'Não foi possível completar o cadastro.')
        return redirect('cadastro:register')
    else:
        form = RegisterUserForm()
        return render(request, 'cadastro/register.html', {})

def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('invest:home')
        else:
            messages.success(request, 'Login inválido.')
            return redirect('cadastro:login')
    else:
        return render(request, 'cadastro/login.html', {})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Sua senha foi alterada com sucesso.')
            return redirect('cadastro:change_password')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'cadastro/change_password.html', {'form': form})
