"""solutionup URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from produtos.views import catalogo_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('produtos.urls.catalogo_url')),
    path('pedidos/', include('vendas.urls.pedido_url')),
    path('produtos/', include('produtos.urls.produtos_url')),
    path('funcionarios/', include('vendas.urls.funcionarios_url')),
    path('fornecedores/', include('produtos.urls.fornecedores_url')),
    path('clientes/', include('vendas.urls.clientes_url')),
    path('pedidos/', include('vendas.urls.pedido_url')),
    path('auth/', include('users.urls.auth_url')),
    path('api/', include('api.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)