from django.contrib import admin
from .models import Jogo, Jogador, Gol, Escalacao, OutrosJogos

admin.site.register(Jogo)
admin.site.register(Jogador)
admin.site.register(Gol)
admin.site.register(Escalacao)
admin.site.register(OutrosJogos)
