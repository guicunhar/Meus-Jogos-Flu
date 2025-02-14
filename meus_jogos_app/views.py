import pandas as pd
from django.shortcuts import render
from .models import Jogo, Gol, Escalacao
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

def estatisticas_gerais(request):
    gols = Gol.objects.all()

    data_gols = {
        "autor_gol": [gol.autor_gol for gol in gols],
        "assistencia": [gol.assistencia for gol in gols],
    }

    escalacoes_jog = Escalacao.objects.exclude(jogador__icontains="TEC")
    escalacoes_tec = Escalacao.objects.filter(jogador__icontains="TEC")

    data_escalacao = {
        "jogador": [esc.jogador for esc in escalacoes_jog]
    }

    data_tec = {
        "jogador": [esc.jogador for esc in escalacoes_tec]
    }

    df_gols = pd.DataFrame(data_gols)
    
    df_gols = df_gols["autor_gol"].value_counts().reset_index()
    df_gols.columns = ["Jogador", "Gols"]

    df_assists = pd.DataFrame(data_gols)
    df_assists = df_assists["assistencia"].value_counts().reset_index()
    df_assists = df_assists.drop(0)
    df_assists.columns = ["Jogador", "Assists"]

    df_part = pd.DataFrame(data_gols)
    df_part = df_part[~df_part["autor_gol"].str.contains("Contra", na=False)]
    top_goleadores = df_part["autor_gol"].value_counts().rename("gols")
    top_assists = df_part["assistencia"].value_counts().rename("assist")  
    top_participacao = pd.concat([top_goleadores, top_assists], axis=1).fillna(0)
    top_participacao["g/a"] = top_participacao["gols"] + top_participacao["assist"]
    top_participacao = top_participacao.sort_values(by="g/a", ascending=False).astype(int)
    top_participacao = top_participacao.reset_index()
    top_participacao.index = range(1, len(top_participacao) + 1)
    top_participacao.columns = ["jogador", "gols","assists","g/a"]
    top_participacao = top_participacao[["jogador","g/a","gols","assists"]]
    df_part = top_participacao
    df_part = df_part.iloc[1:].reset_index(drop=True)
    df_part.columns = ["Jogador", "G/A","Gols","Assists"]

    df_dupla =  pd.DataFrame(data_gols)
    gols_sem_na = df_dupla[df_dupla['assistencia'] != ""].copy()
    gols_sem_na["dupla"] = gols_sem_na.apply(lambda row: f"G: {row['autor_gol']} - A: {row['assistencia']}", axis=1)
    duplas_count = gols_sem_na["dupla"].value_counts().reset_index()
    duplas_count.columns = ["dupla", "gols"]
    df_dupla = duplas_count
    df_dupla.columns = ["Dupla", "Gols"]

    df_mais_jogos =  pd.DataFrame(data_escalacao)
    df_mais_jogos = df_mais_jogos["jogador"].value_counts().reset_index()
    df_mais_jogos.columns = ["Técnico", "Jogos"]
    
    df_mais_tec =  pd.DataFrame(data_tec)
    df_mais_tec = df_mais_tec["jogador"].value_counts().reset_index()
    df_mais_tec.columns = ["Técnico", "Jogos"]


    context = {'df_gols': df_gols.to_html(index=False),
               'df_assists': df_assists.to_html(index=False),
               'df_part': df_part.to_html(index=False),
               'df_dupla': df_dupla.to_html(index=False),
               'df_mais_jogos': df_mais_jogos.to_html(index=False),
               'df_mais_tec': df_mais_tec.to_html(index=False)}

    return render(request, 'meus_jogos_app/estatisticas_gerais.html', context)