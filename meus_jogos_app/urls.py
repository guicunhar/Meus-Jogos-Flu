from django.contrib import admin
from django.urls import path
from meus_jogos_app.views import lista_jogos, lista_outros_jogos,jogos_importantes,estatisticas_jogadores, estatisticas_gerais,estatisticas_adv,estatisticas_datas,jogadores_importantes

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lista_jogos, name='home'),  
    path('jogos/jogos_flu', lista_jogos, name='jogos_flu'),
    path('jogos/outros_jogos', lista_outros_jogos, name='outros_jogos'),
    path('hall_da_fama/jogos_importantes', jogos_importantes, name='jogos_importantes'),
    path('hall_da_fama/jogadores_importantes', jogadores_importantes, name='jogadores_importantes'),
    path('estatisticas/dados_gerais/', estatisticas_gerais, name='estatisticas_dados_gerais'),
    path('estatisticas/dados_jogadores/', estatisticas_jogadores, name='estatisticas_dados_jogadores'),
    path('estatisticas/dados_adv/', estatisticas_adv, name='estatisticas_dados_adv'),
    path('estatisticas/dados_datas/', estatisticas_datas, name='estatisticas_dados_datas'),
]
