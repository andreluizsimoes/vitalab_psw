from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate, login

# Create your views here.
def cadastro(request):

    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":        
        primeiro_nome = request.POST.get('primeiro_nome')
        ultimo_nome = request.POST.get('ultimo_nome')
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        email = request.POST.get('email')
        confirmar_senha = request.POST.get('confirmar_senha')


        def username_existe(username):
            # Tenta encontrar um usuário com o mesmo username na base de dados
            try:
                user = User.objects.get(username=username)
                messages.add_message(request, constants.ERROR, 'Este nome de usuário já existe!')
                return True  # Se encontrar um usuário, retorna True (já existe)
            except User.DoesNotExist:
                return False  # Se não encontrar, retorna False (não existe)

        if not username_existe(username):
            if not senha == confirmar_senha:
                messages.add_message(request, constants.ERROR, 'As senhas não coincidem!')
                return redirect('/usuarios/cadastro')
            
            if len(senha) < 6:
                messages.add_message(request, constants.ERROR, 'Sua senha deve ter no mínimo 6 digitos!')
                return redirect('/usuarios/cadastro')           
            
            try:
                user = User.objects.create_user(
                    username = username,
                    password = senha,
                    email = email,
                    first_name = primeiro_nome,
                    last_name = ultimo_nome
                )
                messages.add_message(request, constants.SUCCESS, 'Usuário cadastrado com sucesso!')
            except:
                messages.add_message(request, constants.ERROR, 'Erro inteno do sistema. Contacte um administrador.')
                return redirect('/usuarios/cadastro')



        return redirect('/usuarios/cadastro')
    
def logar(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        user = authenticate(username=username, password=senha)
        if user:
            login(request, user)
            # Acontecerá um erro ao redirecionar por enquanto, resolveremos nos próximos passos
            return redirect('/')
        else:
            messages.add_message(request, constants.ERROR, 'Usuario ou senha inválidos')
            return redirect('/usuarios/login')
