from django.contrib import admin
from django.urls import path
from meus_jogos_app.views import lista_jogos, estatisticas_gerais

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lista_jogos, name='home'),  
    path('jogos/', lista_jogos, name='jogos'),
    path('estatisticas/dados_gerais/', estatisticas_gerais, name='estatisticas_dados_gerais'),
    path('estatisticas/dados_jogadores/', estatisticas_gerais, name='estatisticas_dados_jogadores'),
]
