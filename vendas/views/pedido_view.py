import csv
from datetime import datetime
from django.http import FileResponse, HttpResponse
from django.contrib.messages.api import success
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from vendas.forms import FormPedido, FormPedidoItem
from vendas.models import Pedido, PedidoItem, Funcionario
from django.http import Http404

class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    paginate_by = 100
    template_name = 'pedido/pedido_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q') or ''
        object_list = self.model.objects.filter(
            Q(id__icontains=query) |
            Q(cliente__nome__icontains=query) |
            Q(cliente__cpf__icontains=query)
        )
        return object_list.order_by('-data_cadastro')

class PedidoDetailView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'pedido/pedido_detail.html'

@login_required
def adicionar_pedido(request):
    form_pedido = FormPedido(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form_pedido.is_valid():
            new_pedido = form_pedido.save()
            messages.add_message(request, messages.SUCCESS, 'Agora insira os itens do pedido!', extra_tags='success')
            return redirect(f'/pedidos/alterar/{new_pedido.id}')
        else:
            messages.add_message(request, messages.ERROR, 'Erro no formulário, tente novamente!', extra_tags='danger')       
    return render(request, 'pedido/pedido_add.html', {'form_pedido': form_pedido})

@login_required
def remover_pedido(request, id):
    if request.method == 'GET':
        pedido = Pedido.objects.get(id=id)
        itens = PedidoItem.objects.filter(pedido=id)
        for item in itens:
            item.produto.quantidade += item.quantidade
            item.produto.save()
        comprovante = Pedido.objects.get(id=pedido.id).comprovante.name
        if comprovante:
            pedido.comprovante.storage.delete(pedido.comprovante.name)
        pedido.delete()
        return redirect('/pedidos')
    else:
        return render(request, 'pedido/pedido_list.html')

@login_required
def alterar_pedido(request, id):
    instance = get_object_or_404(Pedido, id=id)
    pedido = Pedido.objects.get(id=id)
    itens = PedidoItem.objects.filter(pedido=id)
    total_itens = pedido.get_total_itens()
    form_pedido = FormPedido(request.POST or None, request.FILES or None, instance=instance)
    form_item = FormPedidoItem(request.POST or None)
    if request.method == 'POST':
        if form_pedido.is_valid():
            old_comprovante = Pedido.objects.get(id=pedido.id).comprovante.name
            if not old_comprovante:
                form_pedido.save()
            elif form_pedido.cleaned_data['comprovante'] != old_comprovante:
                pedido.comprovante.storage.delete(pedido.comprovante.name)           
            form_pedido.save()
            messages.add_message(request, messages.SUCCESS, 'Pedido alterado!', extra_tags='success')
            return redirect(f'/pedidos/alterar/{pedido.id}')
        else:
            messages.add_message(request, messages.ERROR, 'Erro no formulário, tente novamente!', extra_tags='danger')
            return render(request, 'pedido/pedido_edit.html', {'form': form_pedido})
    else:
        return render(request, 'pedido/pedido_edit.html', {'form_pedido': form_pedido, 'form_item' : form_item, 'pedido': pedido, 'itens': itens, 'total_itens': total_itens})

@login_required
def alterar_item(request, id_pedido):
    pedido = Pedido.objects.get(id=id_pedido)
    form_item = FormPedidoItem(request.POST or None)
    if request.method == 'POST':
        if form_item.is_valid():
            new_item = PedidoItem(
                pedido=pedido,
                produto=form_item.cleaned_data['produto'],
                quantidade=form_item.cleaned_data['quantidade']
            )
            if new_item.quantidade > new_item.produto.quantidade:
                messages.add_message(request, messages.ERROR, 'Quantidade de produtos informada maior que a disponível!', extra_tags='danger')
            else:
                new_item.produto.quantidade -= new_item.quantidade
                new_item.produto.save()
                
                item = PedidoItem.objects.filter(pedido=pedido, produto=new_item.produto)
                if item:
                    item[0].quantidade += new_item.quantidade
                    item[0].save() 
                else:
                    new_item.produto.save()
                    new_item.save()    
    return redirect(f'/pedidos/alterar/{id_pedido}')

@login_required
def remover_item(request, id_pedido, id_item):
    if request.method == 'GET':
        try:
            item = PedidoItem.objects.get(id=id_item)
            messages.add_message(request, messages.SUCCESS, 'Item removido!', extra_tags='success')
        except:
            messages.add_message(request, messages.ERROR, 'Não foi possível remover item do pedido!', extra_tags='danger')
            return redirect('/pedidos')                                    
        item.produto.quantidade += item.quantidade
        item.produto.save()
        item.delete()     
        return redirect(f'/pedidos/alterar/{id_pedido}')

@login_required
def adicionar_filtro(request):
    if request.user.has_perm('vendas.view_pedido'):
        data_inicial = datetime.strptime(request.POST.get('data_inicio'), '%Y-%m-%d')
        data_final = datetime.strptime(request.POST.get('data_final') + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        if request.method == 'POST':
            pedidos = Pedido.objects.filter(data_cadastro__gte=data_inicial, data_cadastro__lte=data_final)
            if pedidos:
                response = HttpResponse(                
                    content_type='text/csv',
                    headers={'Content-Disposition': f'attachment; filename="relatorio_pedidos_{datetime.now().strftime("%d/%m/%Y")}.csv"'},
                )
                writer = csv.writer(response, delimiter=';')
                writer.writerow(['Pedido', 'Data de Cadastro', 'Funcionario', 'Valor Total'])
                for pedido in pedidos:
                    writer.writerow([pedido.id, pedido.data_cadastro.strftime('%d/%m/%Y'), pedido.funcionario.nome, pedido.get_total_itens()])
                    messages.add_message(request, messages.SUCCESS, 'Relátorio gerado com sucesso!', extra_tags='success')
                return response
            else:
                messages.add_message(request, messages.ERROR, 'Nenhum pedido encontrado neste período!', extra_tags='danger')
        return redirect('/pedidos')
    return redirect('/')
