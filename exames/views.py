from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import TiposExames

@login_required
def solicitar_exames(request):
    if request.method == "GET":
        tipos_exames = TiposExames.objects.all()
        return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames})