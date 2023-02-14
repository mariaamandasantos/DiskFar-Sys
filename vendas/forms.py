from django.db.models.fields import CharField, DateField
from django.forms import ModelForm, DateInput, Select, EmailInput, TextInput, NumberInput, Textarea, FileInput

from .models import Clientes, Cargo, Funcionario, Pedido, PedidoItem

class FormCliente(ModelForm):
    class Meta:
        model = Clientes
        fields = '__all__'
        widgets = {
            'nome': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Nome do cliente'
            }),
            'cpf': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'CPF do cliente',
                'minlength': "11"
            }),
            'email': EmailInput(attrs={
                'class': "form-control",
                'placeholder': 'E-mail'
            }),        
            'telefone': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Insira o Telefone'
            }),
            'celular': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Insira o Celular'
            })
        }

class FormCargo(ModelForm):
    class Meta:
        model = Cargo
        fields = '__all__'
        widgets = {      
            'nome': TextInput(attrs={
            'class': "form-control",
            'placeholder': 'Nome do cargo'
            })
        }

class FormFuncionario(ModelForm):
    class Meta:
        model = Funcionario
        fields = '__all__'
        widgets = {
            'nome': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Nome do funcionario'
            }),
            'cpf': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'CPF do funcionario',
                'maxlength': 14
            }),
            'data_nascimento': DateInput( 
                format=('%Y-%m-%d'),
                attrs={
                    'class': "form-control",
                    'type': 'date'
                }
            ),
            'percentual_comissao': NumberInput(attrs={
                'class': "form-control",
                'placeholder': 'Percentual'
            }),
            'usuario': Select(attrs={
                'class': "form-select",
                'placeholder': 'Selecione o usuário'
            }),
            'cargo': Select(attrs={
                'class': "form-select",
                'placeholder': 'Selecione o cargo'
            }),
        }

class FormPedido(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormPedido, self).__init__(*args, **kwargs)

        instance = getattr(self, 'instance', None)
        if instance.id:
            if (self.initial['status'] == 'E' or self.initial['status'] == 'C'):
                for field in ["endereco", "bairro", "numero", "cep", "comprovante", "taxa_entrega", "status", "cliente", "funcionario"]:
                    self.fields[field].widget.attrs['disabled'] = 'disabled'

    class Meta:
        model = Pedido
        fields = '__all__'
        widgets = {
            'cep': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'CEP',
            }),
            'endereco': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Endereço'
            }),
            'bairro': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Bairro'
            }),
            'numero': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Complemento'
            }),
            'comprovante': FileInput(attrs={
                'class': "form-control me-2",
                'style': 'max-width: 300px;'
            }),
            'taxa_entrega': NumberInput(attrs={
                'class': "form-control",
                'placeholder': 'Insira a taxa de entrega'
            }),
            'status': Select(attrs={
                'class': "form-select",
                'placeholder': 'Selecione o status'
            }),
            'cliente': Select(attrs={
                'class': "form-select",
                'placeholder': 'Selecione o cliente'
            }),
            'funcionario': Select(attrs={
                'class': "form-select",
                'placeholder': 'Selecione o funcionário'
            })
        }

class FormPedidoItem(ModelForm):
    class Meta:
        model = PedidoItem
        fields = ['produto', 'quantidade']
        widgets = {
            'produto': Select(attrs={
                'class': "form-control mb-2",
                'max-width': '200px', 
            }),
            'quantidade': NumberInput(attrs={
                'class': "form-control mb-2",
                'step' : 1,
                'min' : 1
            })
        }
