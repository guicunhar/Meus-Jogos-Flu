import pandas as pd
from django.shortcuts import render
from .models import Jogo, Gol, Escalacao, OutrosJogos
from collections import Counter

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
                f"{autor} ({count})" if count > 1 else autor
                for autor, count in Counter([gol.autor_gol.strip() for gol in jogo.gols.all()]).items()
            ])
            for jogo in jogos
        ]

    }

    df_jogos = pd.DataFrame(data)
    df_jogos['publico'] = df_jogos['publico'].apply(lambda x: f"{x:,}".replace(",","."))
    df_jogos.columns = ["ID", "","Placar","Adversário","Estádio","Data","Campeonato","Árbritro","Público","Gols"]
    df_jogos= df_jogos.sort_values(by="ID", ascending=False)    

    context = {'df_jogos': df_jogos.to_html(index=False)}
    return render(request, 'meus_jogos_app/jogos_flu.html', context)

def lista_outros_jogos(request):
    jogos = OutrosJogos.objects.all()
    
    data = {
        "id": [jogo.id for jogo in jogos],
        "mandante": [jogo.mandante for jogo in jogos],
        "placar": [f"{jogo.gols_mandante} x {jogo.gols_visitante}" for jogo in jogos],
        "visitante": [jogo.visitante for jogo in jogos],
        "estadio": [f"{jogo.estadio} ({jogo.local_estadio})" for jogo in jogos],
        "data": [jogo.data.strftime("%d/%m/%Y") for jogo in jogos],
        "campeonato": [jogo.campeonato for jogo in jogos],
    }

    df_outros_jogos = pd.DataFrame(data)
    df_outros_jogos.columns = ["ID", "Mandante","Placar","Visitante","Estádio","Data","Campeonato"]
    df_outros_jogos= df_outros_jogos.sort_values(by="ID", ascending=False)

    context = {'df_outros_jogos': df_outros_jogos.to_html(index=False)}
    return render(request, 'meus_jogos_app/outros_jogos.html', context)

def jogos_importantes(request):
    context = {}
    return render(request, 'meus_jogos_app/jogos_importantes.html', context)

def jogadores_importantes(request):
    context = {}
    return render(request, 'meus_jogos_app/jogadores_importantes.html', context)

def estatisticas_jogadores(request):
    gols = Gol.objects.all()

    data_gols = {
        "autor_gol": [gol.autor_gol for gol in gols],
        "assistencia": [gol.assistencia for gol in gols],
    }

    jogos = Jogo.objects.all()

    data_jogos = {
        "id": [jogo.id for jogo in jogos],
        "fluminense": "Fluminense",
        "gols_flu": [jogo.gols_flu for jogo in jogos],
        "gols_adv": [jogo.gols_adv for jogo in jogos],
        "placar": [f"{jogo.gols_flu} x {jogo.gols_adv}" for jogo in jogos],
        "adversario": [f"{jogo.adversario} ({jogo.local_adv})" for jogo in jogos],
        "estadio": [f"{jogo.estadio} ({jogo.local_estadio})" for jogo in jogos],
        "local_estadio": [jogo.local_estadio for jogo in jogos],
        "data": [jogo.data.strftime("%d/%m/%Y") for jogo in jogos],
        "ano": [jogo.data.strftime("%Y") for jogo in jogos],
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
    df_gols.index = range(1, len(df_gols) + 1)

    df_assists = pd.DataFrame(data_gols)
    df_assists = df_assists["assistencia"].value_counts().reset_index()
    df_assists = df_assists.drop(0)
    df_assists.columns = ["Jogador", "Assists"]
    df_assists.index = range(1, len(df_assists) + 1)

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
    df_part.index = range(1, len(df_part) + 1)

    df_dupla =  pd.DataFrame(data_gols)
    gols_sem_na = df_dupla[df_dupla['assistencia'] != ""].copy()
    gols_sem_na["dupla"] = gols_sem_na.apply(lambda row: f"G: {row['autor_gol']} - A: {row['assistencia']}", axis=1)
    duplas_count = gols_sem_na["dupla"].value_counts().reset_index()
    duplas_count.columns = ["dupla", "gols"]
    df_dupla = duplas_count
    df_dupla.columns = ["Dupla", "Gols"]
    df_dupla.index = range(1, len(df_dupla) + 1)

    df_mais_jogos =  pd.DataFrame(data_escalacao)
    df_mais_jogos = df_mais_jogos["jogador"].value_counts().reset_index()
    df_mais_jogos.columns = ["Jogador", "Jogos"]
    df_mais_jogos.index = range(1, len(df_mais_jogos) + 1)
    
    df_mais_tec =  pd.DataFrame(data_tec)
    df_mais_tec = df_mais_tec["jogador"].value_counts().reset_index()
    df_mais_tec.columns = ["Técnico", "Jogos"]
    df_mais_tec.index = range(1, len(df_mais_tec) + 1)

    df_art_ano_jogos = pd.DataFrame(data_jogos)

    df_art_ano_gols = pd.DataFrame({
        "id_jogo": [gol.id_jogo.id for gol in Gol.objects.all()],
        "autor_gol": [gol.id_autor.jogador for gol in Gol.objects.all()],
    })

    df_art_ano = df_art_ano_jogos.merge(df_art_ano_gols, left_on='id', right_on='id_jogo')
    df_art_ano['ano'] = df_art_ano['data'].apply(lambda x: x.split('/')[-1])
    df_art_ano = df_art_ano.groupby(['ano', 'autor_gol']).size().reset_index(name='gols')
    df_art_ano = df_art_ano.sort_values(by=['gols'], ascending=[False])
    df_art_ano.columns = ["Ano", "Jogador", "Gols"]
    df_art_ano.index = range(1, len(df_art_ano) + 1)

    df_art_time = df_art_ano_jogos.merge(df_art_ano_gols, left_on='id', right_on='id_jogo')
    df_art_time = df_art_time.groupby(['adversario', 'autor_gol']).size().reset_index(name='gols')
    df_art_time = df_art_time.sort_values(by=['gols'], ascending=[False])
    df_art_time.columns = ["Adversário", "Jogador", "Gols"]
    df_art_time.index = range(1, len(df_art_time) + 1)

    context = {'df_gols': df_gols.to_html(index=True),
               'df_assists': df_assists.to_html(index=True),
               'df_part': df_part.to_html(index=True),
               'df_dupla': df_dupla.to_html(index=True),
               'df_mais_jogos': df_mais_jogos.to_html(index=True),
               'df_mais_tec': df_mais_tec.to_html(index=True),
               'df_art_ano': df_art_ano.to_html(index=True),
               'df_art_time': df_art_time.to_html(index=True)}

    return render(request, 'meus_jogos_app/estatisticas_jogadores.html', context)

def estatisticas_gerais(request):
    jogos = Jogo.objects.all()

    data_jogos = {
        "id": [jogo.id for jogo in jogos],
        "fluminense": "Fluminense",
        "gols_flu": [jogo.gols_flu for jogo in jogos],
        "gols_adv": [jogo.gols_adv for jogo in jogos],
        "placar": [f"{jogo.gols_flu} x {jogo.gols_adv}" for jogo in jogos],
        "adversario": [f"{jogo.adversario} ({jogo.local_adv})" for jogo in jogos],
        "estadio": [f"{jogo.estadio} ({jogo.local_estadio})" for jogo in jogos],
        "local_estadio": [jogo.local_estadio for jogo in jogos],
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

    data_jogos["resultado"] = [
    "V" if gols_flu > gols_adv else "D" if gols_flu < gols_adv else "E"
    for gols_flu, gols_adv in zip(data_jogos["gols_flu"], data_jogos["gols_adv"])
    ]

    df_jogos = pd.DataFrame(data_jogos)
    df_jogos = df_jogos["resultado"].value_counts().reset_index()
    df_jogos = df_jogos.transpose()
    df_jogos.columns = ["V","E","D"]
    df_jogos = df_jogos[1:].reset_index(drop=True)
    df_jogos["Total"] = df_jogos["V"] + df_jogos["E"] + df_jogos["D"]
    aprov = (3*df_jogos["V"] + df_jogos["E"])/(3*(df_jogos["Total"]))*100
    df_jogos["Aprov. %"] = round(float(aprov),2)
    df_gols_total = pd.DataFrame(data_jogos)
    df_gols_total["gols_flu"] = df_gols_total['gols_flu'].sum()
    df_gols_total["gols_adv"] = df_gols_total['gols_adv'].sum()
    df_gols_total = df_gols_total[["gols_flu","gols_adv"]].iloc[:1,:]
    df_gols_total.columns = ["Gols Marcados","Gols Sofridos"]

    df_estado = pd.DataFrame(data_jogos)
    df_estado = df_estado[["local_estadio", "resultado"]]
    df_estado = df_estado.groupby("local_estadio")["resultado"].value_counts().unstack(fill_value=0)
    df_estado["Total"] = df_estado.sum(axis=1)
    df_estado["Aprov. %"] = round((3*df_estado["V"] + df_estado["E"]) / (3*df_estado["Total"])*100,2)
    df_estado = df_estado.reset_index()
    df_estado.columns.name = None
    df_estado = df_estado[["local_estadio", "Total", "V", "E", "D", "Aprov. %"]]
    df_estado = df_estado.rename(columns={"local_estadio": "Estado"})
    df_estado = df_estado.sort_values(by="Total", ascending=False)
    df_estado.index = range(1, len(df_estado) + 1)

    df_estadio = pd.DataFrame(data_jogos)
    df_estadio= df_estadio["estadio"].value_counts().reset_index()
    df_estadio.columns = ["Estádio","Jogos"]
    df_estadio.index = range(1, len(df_estadio) + 1)

    df_arbitro = pd.DataFrame(data_jogos)
    df_arbitro = df_arbitro[["arbitro", "resultado"]]
    df_arbitro = df_arbitro.groupby("arbitro")["resultado"].value_counts().unstack(fill_value=0)
    df_arbitro["Total"] = df_arbitro.sum(axis=1)
    df_arbitro["Aprov. %"] = round((3*df_arbitro["V"] + df_arbitro["E"]) / (3*df_arbitro["Total"])*100,2)
    df_arbitro = df_arbitro.reset_index()
    df_arbitro.columns.name = None
    df_arbitro = df_arbitro[["arbitro", "Total", "V", "E", "D", "Aprov. %"]]
    df_arbitro = df_arbitro.rename(columns={"arbitro": "Árbitro"})
    df_arbitro = df_arbitro.sort_values(by="Total", ascending=False)
    df_arbitro.index = range(1, len(df_arbitro) + 1)

    df_placares = pd.DataFrame(data_jogos)
    df_placares= df_placares["placar"].value_counts().reset_index()
    df_placares.columns = ["Placar","Jogos"]
    df_placares.index = range(1, len(df_placares) + 1)

    df_campeonatos = pd.DataFrame(data_jogos)
    df_campeonatos= df_campeonatos["campeonato"].value_counts().reset_index()
    df_campeonatos.columns = ["Campeonato","Jogos"]
    df_campeonatos.index = range(1, len(df_campeonatos) + 1)

    df_publico = pd.DataFrame(data_jogos)
    df_publico = df_publico[['data', 'placar','adversario','estadio','campeonato','publico']].sort_values(by='publico', ascending=False).reset_index()
    df_publico = df_publico[['data', 'placar','adversario','estadio','campeonato','publico']]
    df_publico['publico'] = df_publico['publico'].apply(lambda x: f"{x:,}".replace(",","."))
    df_publico.columns = ["Data","Placar","Adversário","Estádio","Campeonato","Público"]
    df_publico.index = range(1, len(df_publico) + 1)



    context = {'df_jogos': df_jogos.to_html(index=False),
               'df_gols_total': df_gols_total.to_html(index=False),
               'df_estado': df_estado.to_html(index=True),
               'df_estadio': df_estadio.to_html(index=True),
               'df_arbitro': df_arbitro.to_html(index=True),
               'df_placares': df_placares.to_html(index=True),
               'df_campeonatos': df_campeonatos.to_html(index=True),
               'df_publico': df_publico.to_html(index=True)}

    return render(request, 'meus_jogos_app/estatisticas_gerais.html', context)

def estatisticas_adv(request):
    jogos = Jogo.objects.all()
    
    data_jogos = {
        "id": [jogo.id for jogo in jogos],
        "fluminense": "Fluminense",
        "gols_flu": [jogo.gols_flu for jogo in jogos],
        "gols_adv": [jogo.gols_adv for jogo in jogos],
        "placar": [f"{jogo.gols_flu} x {jogo.gols_adv}" for jogo in jogos],
        "local_adv": [jogo.local_adv for jogo in jogos],
        "adversario": [f"{jogo.adversario} ({jogo.local_adv})" for jogo in jogos],
        "estadio": [f"{jogo.estadio} ({jogo.local_estadio})" for jogo in jogos],
        "local_estadio": [jogo.local_estadio for jogo in jogos],
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

    data_jogos["resultado"] = [
    "V" if gols_flu > gols_adv else "D" if gols_flu < gols_adv else "E"
    for gols_flu, gols_adv in zip(data_jogos["gols_flu"], data_jogos["gols_adv"])
    ]


    df_adversarios = pd.DataFrame(data_jogos)
    df_adversarios = df_adversarios[["adversario", "resultado"]]
    df_adversarios = df_adversarios.groupby("adversario")["resultado"].value_counts().unstack(fill_value=0)
    df_adversarios["Total"] = df_adversarios.sum(axis=1)
    df_adversarios["Aprov. %"] = round((3*df_adversarios["V"] + df_adversarios["E"]) / (3*df_adversarios["Total"])*100,2)
    df_adversarios = df_adversarios.reset_index()
    df_adversarios.columns.name = None
    df_adversarios = df_adversarios[["adversario", "Total", "V", "E", "D", "Aprov. %"]]
    df_adversarios = df_adversarios.rename(columns={"adversario": "Adversário"})
    df_adversarios = df_adversarios.sort_values(by="Total", ascending=False)
    df_adversarios.index = range(1, len(df_adversarios) + 1)

    df_local_adv = pd.DataFrame(data_jogos)
    df_local_adv = df_local_adv[["local_adv", "resultado"]]
    df_local_adv = df_local_adv.groupby("local_adv")["resultado"].value_counts().unstack(fill_value=0)
    df_local_adv["Total"] = df_local_adv.sum(axis=1)
    df_local_adv["Aprov. %"] = round((3*df_local_adv["V"] + df_local_adv["E"]) / (3*df_local_adv["Total"])*100,2)
    df_local_adv = df_local_adv.reset_index()
    df_local_adv.columns.name = None
    df_local_adv = df_local_adv[["local_adv", "Total", "V", "E", "D", "Aprov. %"]]
    df_local_adv = df_local_adv.rename(columns={"local_adv": "Local do Adv."})
    df_local_adv = df_local_adv.sort_values(by="Total", ascending=False)
    df_local_adv.index = range(1, len(df_local_adv) + 1)

    context = {'df_adversarios': df_adversarios.to_html(index=True),
                'df_local_adv': df_local_adv.to_html(index=True),}

    return render(request, 'meus_jogos_app/estatisticas_adversarios.html', context)

def estatisticas_datas(request):
    jogos = Jogo.objects.all()
    
    data_jogos = {
        "id": [jogo.id for jogo in jogos],
        "fluminense": "Fluminense",
        "gols_flu": [jogo.gols_flu for jogo in jogos],
        "gols_adv": [jogo.gols_adv for jogo in jogos],
        "placar": [f"{jogo.gols_flu} x {jogo.gols_adv}" for jogo in jogos],
        "local_adv": [jogo.local_adv for jogo in jogos],
        "adversario": [f"{jogo.adversario} ({jogo.local_adv})" for jogo in jogos],
        "estadio": [f"{jogo.estadio} ({jogo.local_estadio})" for jogo in jogos],
        "local_estadio": [jogo.local_estadio for jogo in jogos],
        "data": [jogo.data.strftime("%d/%m/%Y") for jogo in jogos],
        "ano": [jogo.data.strftime("%Y") for jogo in jogos],
        "mes": [jogo.data.strftime("%m") for jogo in jogos],
        "dia": [jogo.data.strftime("%d") for jogo in jogos],
        "dia_da_semana": [jogo.data.weekday() for jogo in jogos],
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

    data_jogos["resultado"] = [
    "V" if gols_flu > gols_adv else "D" if gols_flu < gols_adv else "E"
    for gols_flu, gols_adv in zip(data_jogos["gols_flu"], data_jogos["gols_adv"])
    ]

    meses_map = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
            7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
    
    dias_map = {
            0: 'Segunda-Feira', 1: 'Terça-Feira', 2: 'Quarta-Feira', 3: 'Quinta-Feira', 4: 'Sexta-Feira', 5: 'Sábado', 6: 'Domingo'
            }
     
    
    df_mes= pd.DataFrame(data_jogos)
    df_mes['mes'] = df_mes['mes'].astype(int).map(meses_map)
    df_mes = df_mes[["mes", "resultado"]]
    df_mes = df_mes.groupby("mes")["resultado"].value_counts().unstack(fill_value=0)
    df_mes["Total"] = df_mes.sum(axis=1)
    df_mes["Aprov. %"] = round((3*df_mes["V"] + df_mes["E"]) / (3*df_mes["Total"])*100,2)
    df_mes = df_mes.reset_index()
    df_mes.columns.name = None
    df_mes = df_mes[["mes", "Total", "V", "E", "D", "Aprov. %"]]
    df_mes = df_mes.rename(columns={"mes": "Mês"})
    df_mes = df_mes.sort_values(by="Total", ascending=False)
    df_mes.index = range(1, len(df_mes) + 1)

    df_ano= pd.DataFrame(data_jogos)
    df_ano = df_ano[["ano", "resultado"]]
    df_ano = df_ano.groupby("ano")["resultado"].value_counts().unstack(fill_value=0)
    df_ano["Total"] = df_ano.sum(axis=1)
    df_ano["Aprov. %"] = round((3*df_ano["V"] + df_ano["E"]) / (3*df_ano["Total"])*100,2)
    df_ano = df_ano.reset_index()
    df_ano.columns.name = None
    df_ano = df_ano[["ano", "Total", "V", "E", "D", "Aprov. %"]]
    df_ano = df_ano.rename(columns={"ano": "Ano"})
    df_ano = df_ano.sort_values(by="Total", ascending=False)
    df_ano.index = range(1, len(df_ano) + 1)

    df_dia= pd.DataFrame(data_jogos)
    df_dia = df_dia[["dia", "resultado"]]
    df_dia = df_dia.groupby("dia")["resultado"].value_counts().unstack(fill_value=0)
    df_dia["Total"] = df_dia.sum(axis=1)
    df_dia["Aprov. %"] = round((3*df_dia["V"] + df_dia["E"]) / (3*df_dia["Total"])*100,2)
    df_dia = df_dia.reset_index()
    df_dia.columns.name = None
    df_dia = df_dia[["dia", "Total", "V", "E", "D", "Aprov. %"]]
    df_dia = df_dia.rename(columns={"dia": "Dia"})
    df_dia = df_dia.sort_values(by="Total", ascending=False)
    df_dia.index = range(1, len(df_dia) + 1)

    
    df_dia_semana= pd.DataFrame(data_jogos)
    df_dia_semana = df_dia_semana[["dia_da_semana", "resultado"]]
    df_dia_semana['dia_da_semana'] = df_dia_semana['dia_da_semana'].astype(int).map(dias_map)
    df_dia_semana = df_dia_semana.groupby("dia_da_semana")["resultado"].value_counts().unstack(fill_value=0)
    df_dia_semana["Total"] = df_dia_semana.sum(axis=1)
    df_dia_semana["Aprov. %"] = round((3*df_dia_semana["V"] + df_dia_semana["E"]) / (3*df_dia_semana["Total"])*100,2)
    df_dia_semana = df_dia_semana.reset_index()
    df_dia_semana.columns.name = None
    df_dia_semana = df_dia_semana[["dia_da_semana", "Total", "V", "E", "D", "Aprov. %"]]
    df_dia_semana = df_dia_semana.rename(columns={"dia_da_semana": "Dia da Semana"})
    df_dia_semana = df_dia_semana.sort_values(by="Total", ascending=False)
    df_dia_semana.index = range(1, len(df_dia_semana) + 1)

    context = {'df_mes': df_mes.to_html(index=True),
               'df_ano': df_ano.to_html(index=True),
               'df_dia': df_dia.to_html(index=True),
               'df_dia_semana': df_dia_semana.to_html(index=True)}
    return render(request, 'meus_jogos_app/estatisticas_datas.html', context)
