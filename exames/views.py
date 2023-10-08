from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import TiposExames, PedidosExames, SolicitacaoExame
from datetime import datetime
from django.contrib.messages import constants
from django.contrib import messages

@login_required
def solicitar_exames(request):
    tipos_exames = TiposExames.objects.all()
    if request.method == "GET":
        return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames})
    elif request.method == "POST":
        #TODO: Adicionar a data da solicitação
        # Obtém a data atual
        data_atual = datetime.now()

        # Dicionário para mapear meses
        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }

        # Formata a data no formato "dia de mês"
        data_formatada = f"{data_atual.strftime('%d')} de {meses[data_atual.month]}"


        # Lista de ids dos exames
        exames_id = request.POST.getlist('exames')
        solicitacao_exames = TiposExames.objects.filter(id__in=exames_id)

        #TODO: Calcular preço apenas dos exames disponíveis
        preco_total = 0
        for exame in solicitacao_exames:
            if exame.disponivel:
                preco_total += exame.preco
            
        
        return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames, 
                                                         'solicitacao_exames': solicitacao_exames,
                                                         'preco_total': preco_total,
                                                         'data': data_formatada})

@login_required
def fechar_pedido(request):
    exames_id = request.POST.getlist('exames')

    solicitacao_exames = TiposExames.objects.filter(id__in=exames_id)

    pedido_exame = PedidosExames(
        usuario = request.user,
        data=datetime.now(),
    )
    pedido_exame.save()

    for exame in solicitacao_exames:
        solicitacao_exame_temp = SolicitacaoExame(
        usuario = request.user,
        exame=exame,
        status = 'E'
        )
        solicitacao_exame_temp.save()
        pedido_exame.exames.add(solicitacao_exame_temp)
    
    pedido_exame.save()

    messages.add_message(request, constants.SUCCESS, 'Pedido de Exames enviado com sucesso!')
    return redirect('/exames/gerenciar_pedidos/')

@login_required
def gerenciar_pedidos(request):
    pedidos_exames = PedidosExames.objects.filter(usuario=request.user)
    return render(request, 'gerenciar_pedidos.html', {'pedidos_exames': pedidos_exames})

@login_required
def cancelar_pedido(request, pedido_id):
    pedido = PedidosExames.objects.get(id=pedido_id)

    if not pedido.usuario == request.user:
        messages.add_message(request, constants.ERROR, 'Não pode cancelar este pedido, ele não é seu!')
        return redirect('/exames/gerenciar_pedidos/')

    pedido.agendado = False
    pedido.save()
    messages.add_message(request, constants.SUCCESS, 'Pedido cancelado com sucesso!')
    return redirect('/exames/gerenciar_pedidos/')

@login_required
def gerenciar_exames(request):
    exames = SolicitacaoExame.objects.filter(usuario=request.user)

    return render(request, 'gerenciar_exames.html', {'exames': exames})

@login_required
def permitir_abrir_exame(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)
		#TODO: validar se o exame é do usuário
    if not exame.usuario == request.user:
        messages.add_message(request, constants.ERROR, 'EPA! Não pode visualizar exame que não é seu!')
        return redirect('/exames/gerenciar_exames/')

    if not exame.requer_senha:
        # verificar se o pdf existe
        if exame.resultado:
            return redirect(exame.resultado.url)
        else:
            messages.add_message(request, constants.ERROR, 'Não há arquivo cadastrado em nossa base de dados')
            return redirect('/exames/gerenciar_exames/')
    else: 
        return redirect(f'/exames/solicitar_senha_exame/{exame.id}')
    
@login_required
def solicitar_senha_exame(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)
    if not exame.usuario == request.user:
        messages.add_message(request, constants.ERROR, 'EPA! Não pode visualizar exame que não é seu!')
        return redirect('/exames/gerenciar_exames/')
    
    if request.method == "GET":
        return render(request, 'solicitar_senha_exame.html', {'exame': exame})
    elif request.method == "POST":
        senha = request.POST.get("senha")
				#TODO: validar se o exame é do usuário
        if senha == exame.senha:
            return redirect(exame.resultado.url)
        else:
            messages.add_message(request, constants.ERROR, 'Senha inválida!')
            return redirect(f'/exames/solicitar_senha_exame/{exame.id}')