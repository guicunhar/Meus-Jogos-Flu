from django.contrib import admin
from django.urls import path
from meus_jogos_app.views import lista_jogos, estatisticas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lista_jogos, name='home'),  
    path('jogos/', lista_jogos, name='jogos'),
    path('estatisticas/', estatisticas, name='estatisticas'),
]
