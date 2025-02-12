import pandas as pd
from django.shortcuts import render
from .models import Jogo 
from collections import Counter
from datetime import datetime

def lista_jogos(request):
    jogos = Jogo.objects.all()
    
    data = {
        "id": [jogo.id for jogo in jogos],
        "fluminense": "Fluminense",
        "placar": [f"{jogo.gols_flu} x {jogo.gols_adv}" for jogo in jogos],
        "adversario": [f"{jogo.adversario} ({jogo.local_adv})" for jogo in jogos],
        "estadio": [f"{jogo.estadio} ({jogo.local_estadio})" for jogo in jogos],
        "data": [jogo.data.strftime("%d/%m/%Y") for jogo in jogos],
        "campeonato": [jogo.campeonato for jogo in jogos],
        "arbitro": [jogo.arbitro for jogo in jogos],
        "publico": [jogo.publico for jogo in jogos],
        "gols": [
        ', '.join([
            f"{gol} ({count})" if count > 1 else gol
            for gol, count in Counter([gol.autor_gol for gol in jogo.gols.all()]).items()
        ])
        for jogo in jogos
    ]
    }

    df_jogos = pd.DataFrame(data)
    df_jogos['publico'] = df_jogos['publico'].apply(lambda x: f"{x:,}".replace(",","."))
    df_jogos.columns = ["ID", "","Placar","Adversário","Estádio","Data","Campeonato","Árbritro","Público","Gols"]

    context = {'df_jogos': df_jogos.to_html(  index=False)}
    return render(request, 'meus_jogos_app/jogos.html', context)

def estatisticas(request):
    jogos = Jogo.objects.all()
    return render(request, 'meus_jogos_app/estatisticas.html', {'jogos': jogos})