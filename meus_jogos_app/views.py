import pandas as pd
from django.shortcuts import render
from .models import Jogo, Gol, Escalacao, OutrosJogos, Jogador
from collections import Counter
from django.db.models import Q
import json

def lista_jogos(request):
    jogos = Jogo.objects.all().order_by('-id')  # Ordenação no próprio queryset

    data = []
    for jogo in jogos:
        gols = Counter([gol.autor_gol.strip() for gol in jogo.gols.all()])
        gols_formatados = ', '.join(
            f"{autor} ({count})" if count > 1 else autor
            for autor, count in gols.items()
        )

        data.append({
            "id": jogo.id,
            "fluminense": "Fluminense",
            "placar": f"{jogo.gols_flu} x {jogo.gols_adv}",
            "adversario": f"{jogo.adversario} ({jogo.local_adv})",
            "estadio": f"{jogo.estadio} ({jogo.local_estadio})",
            "data": jogo.data.strftime("%d/%m/%Y"),
            "campeonato": jogo.campeonato,
            "publico": f"{jogo.publico:,}".replace(",", "."),
            "gols": gols_formatados,
        })

    context = {'jogos': data}
    return render(request, 'meus_jogos_app/jogos_flu.html', context)

def lista_outros_jogos(request):
    jogos = OutrosJogos.objects.all().order_by('-id')

    data = []
    for jogo in jogos:
        data.append({
            "id": jogo.id,
            "mandante": jogo.mandante,
            "placar": f"{jogo.gols_mandante} x {jogo.gols_visitante}",
            "visitante": jogo.visitante,
            "estadio": f"{jogo.estadio} ({jogo.local_estadio})",
            "data": jogo.data.strftime("%d/%m/%Y"),
            "campeonato": jogo.campeonato,
        })

    context = {'outros_jogos': data}
    return render(request, 'meus_jogos_app/outros_jogos.html', context)

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
        "jogador": [esc.jogador.replace("TEC", "") for esc in escalacoes_tec]
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
    df_part.columns = ["Jogador", "GA","Gols","Assists"]
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
    df_mais_tec.columns = ["Tecnico", "Jogos"]
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
    df_art_ano = df_art_ano[["Jogador","Ano","Gols"]]
    df_art_ano.index = range(1, len(df_art_ano) + 1)

    df_art_time = df_art_ano_jogos.merge(df_art_ano_gols, left_on='id', right_on='id_jogo')
    df_art_time = df_art_time.groupby(['adversario', 'autor_gol']).size().reset_index(name='gols')
    df_art_time = df_art_time.sort_values(by=['gols'], ascending=[False])
    df_art_time.columns = ["Adversario", "Jogador", "Gols"]
    df_art_time = df_art_time[["Jogador","Adversario","Gols"]]
    df_art_time.index = range(1, len(df_art_time) + 1)

    context = {'df_gols': df_gols.to_dict(orient='records'),
               'df_assists': df_assists.to_dict(orient='records'),
               'df_part': df_part.to_dict(orient='records'),
               'df_dupla': df_dupla.to_dict(orient='records'),
               'df_mais_jogos': df_mais_jogos.to_dict(orient='records'),
               'df_mais_tec': df_mais_tec.to_dict(orient='records'),
               'df_art_ano': df_art_ano.to_dict(orient='records'),
               'df_art_time': df_art_time.to_dict(orient='records')}

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
    df_jogos["Aprov"] = round(float(aprov),2)
    df_gols_total = pd.DataFrame(data_jogos)
    df_gols_total["gols_flu"] = df_gols_total['gols_flu'].sum()
    df_gols_total["gols_adv"] = df_gols_total['gols_adv'].sum()
    df_gols_total = df_gols_total[["gols_flu","gols_adv"]].iloc[:1,:]
    df_gols_total.columns = ["GP","GS"]

    df_estado = pd.DataFrame(data_jogos)
    df_estado = df_estado[["local_estadio", "resultado"]]
    df_estado = df_estado.groupby("local_estadio")["resultado"].value_counts().unstack(fill_value=0)
    df_estado["Total"] = df_estado.sum(axis=1)
    df_estado["Aprov"] = round((3*df_estado["V"] + df_estado["E"]) / (3*df_estado["Total"])*100,2)
    df_estado = df_estado.reset_index()
    df_estado.columns.name = None
    df_estado = df_estado[["local_estadio", "Total", "V", "E", "D", "Aprov"]]
    df_estado = df_estado.rename(columns={"local_estadio": "Estado"})
    df_estado = df_estado.sort_values(by="Total", ascending=False)
    df_estado.index = range(1, len(df_estado) + 1)

    df_estadio = pd.DataFrame(data_jogos)
    df_estadio = df_estadio[["estadio", "resultado"]]
    df_estadio= df_estadio.groupby("estadio")["resultado"].value_counts().unstack(fill_value=0)
    df_estadio["Total"] = df_estadio.sum(axis=1)
    df_estadio["Aprov"] = round((3*df_estadio["V"] + df_estadio["E"]) / (3*df_estadio["Total"])*100,2)
    df_estadio = df_estadio.reset_index()
    df_estadio.columns.name = None
    df_estadio.columns = ["estadio","D", "E", "V", "Total", "Aprov"]
    df_estadio = df_estadio.sort_values(by="Total", ascending=False)
    df_estadio.index = range(1, len(df_estadio) + 1)

    df_arbitro = pd.DataFrame(data_jogos)
    df_arbitro = df_arbitro[["arbitro", "resultado"]]
    df_arbitro = df_arbitro.groupby("arbitro")["resultado"].value_counts().unstack(fill_value=0)
    df_arbitro["Total"] = df_arbitro.sum(axis=1)
    df_arbitro["Aprov"] = round((3*df_arbitro["V"] + df_arbitro["E"]) / (3*df_arbitro["Total"])*100,2)
    df_arbitro = df_arbitro.reset_index()
    df_arbitro.columns.name = None
    df_arbitro = df_arbitro[["arbitro", "Total", "V", "E", "D", "Aprov"]]
    df_arbitro = df_arbitro.sort_values(by="Total", ascending=False)
    df_arbitro.index = range(1, len(df_arbitro) + 1)

    df_placares = pd.DataFrame(data_jogos)
    df_placares= df_placares["placar"].value_counts().reset_index()
    df_placares.columns = ["placar","jogos"]
    df_placares.index = range(1, len(df_placares) + 1)

    df_campeonato = pd.DataFrame(data_jogos)
    df_campeonato = df_campeonato[["campeonato", "resultado"]]
    df_campeonato= df_campeonato.groupby("campeonato")["resultado"].value_counts().unstack(fill_value=0)
    df_campeonato["Total"] = df_campeonato.sum(axis=1)
    df_campeonato["Aprov"] = round((3*df_campeonato["V"] + df_campeonato["E"]) / (3*df_campeonato["Total"])*100,2)
    df_campeonato = df_campeonato.reset_index()
    df_campeonato.columns.name = None
    df_campeonato.columns = ["campeonato","D", "E", "V", "Total", "Aprov"]
    df_campeonato = df_campeonato.sort_values(by="Total", ascending=False)
    df_campeonato.index = range(1, len(df_campeonato) + 1)

    df_publico = pd.DataFrame(data_jogos)
    df_publico = df_publico[['data', 'placar','adversario','estadio','campeonato','publico']].sort_values(by='publico', ascending=False).reset_index()
    df_publico = df_publico[['data', 'placar','adversario','estadio','campeonato','publico']]
    df_publico['publico'] = df_publico['publico'].apply(lambda x: f"{x:,}".replace(",","."))
    df_publico.columns = ["data","placar","adversario","estadio","campeonato","publico"]
    df_publico.index = range(1, len(df_publico) + 1)

    context = {'df_jogos': df_jogos.to_dict(orient='records'),
               'df_gols_total': df_gols_total.to_dict(orient='records'),
               'df_estado': df_estado.to_dict(orient='records'),
               'df_estadio': df_estadio.to_dict(orient='records'),
               'df_arbitro': df_arbitro.to_dict(orient='records'),
               'df_placares': df_placares.to_dict(orient='records'),
               'df_campeonato': df_campeonato.to_dict(orient='records'),
               'df_publico': df_publico.to_dict(orient='records')}

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
    df_adversarios["Jogos"] = df_adversarios.sum(axis=1)
    df_adversarios["Aprov"] = round((3*df_adversarios["V"] + df_adversarios["E"]) / (3*df_adversarios["Jogos"])*100,2)
    df_adversarios = df_adversarios.reset_index()
    df_adversarios.columns.name = None
    df_adversarios = df_adversarios[["adversario", "Jogos", "V", "E", "D", "Aprov"]]
    df_adversarios = df_adversarios.sort_values(by="Jogos", ascending=False)
    df_adversarios.index = range(1, len(df_adversarios) + 1)

    df_local_adv = pd.DataFrame(data_jogos)
    df_local_adv = df_local_adv[["local_adv", "resultado"]]
    df_local_adv = df_local_adv.groupby("local_adv")["resultado"].value_counts().unstack(fill_value=0)
    df_local_adv["Jogos"] = df_local_adv.sum(axis=1)
    df_local_adv["Aprov"] = round((3*df_local_adv["V"] + df_local_adv["E"]) / (3*df_local_adv["Jogos"])*100,2)
    df_local_adv = df_local_adv.reset_index()
    df_local_adv.columns.name = None
    df_local_adv = df_local_adv[["local_adv", "Jogos", "V", "E", "D", "Aprov"]]
    df_local_adv = df_local_adv.sort_values(by="Jogos", ascending=False)
    df_local_adv.index = range(1, len(df_local_adv) + 1)

    local_map = {
    'AC': "Acre",
    'AL': "Alagoas",
    'AP': "Amapá",
    'AM': "Amazonas",
    'BA': "Bahia",
    'CE': "Ceará",
    'DF': "Distrito Federal",
    'ES': "Espírito Santo",
    'GO': "Goiás",
    'MA': "Maranhão",
    'MT': "Mato Grosso",
    'MS': "Mato Grosso do Sul",
    'MG': "Minas Gerais",
    'PA': "Pará",
    'PB': "Paraíba",
    'PR': "Paraná",
    'PE': "Pernambuco",
    'PI': "Piauí",
    'RJ': "Rio de Janeiro",
    'RN': "Rio Grande do Norte",
    'RS': "Rio Grande do Sul",
    'RO': "Rondônia",
    'RR': "Roraima",
    'SC': "Santa Catarina",
    'SP': "São Paulo",
    'SE': "Sergipe",
    'TO': "Tocantins",
    'LAS': "América do Sul"
}
    df_local_adv["local_adv"] = df_local_adv["local_adv"].map(local_map)
    
    context = {'df_adversarios': df_adversarios.to_dict(orient='records'),
                'df_local_adv': df_local_adv.to_dict(orient='records'),}

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
    df_mes["Aprov"] = round((3*df_mes["V"] + df_mes["E"]) / (3*df_mes["Total"])*100,2)
    df_mes = df_mes.reset_index()
    df_mes.columns.name = None
    df_mes = df_mes[["mes", "Total", "V", "E", "D", "Aprov"]]
    df_mes = df_mes.sort_values(by="Total", ascending=False)
    df_mes.index = range(1, len(df_mes) + 1)

    df_ano= pd.DataFrame(data_jogos)
    df_ano = df_ano[["ano", "resultado"]]
    df_ano = df_ano.groupby("ano")["resultado"].value_counts().unstack(fill_value=0)
    df_ano["Total"] = df_ano.sum(axis=1)
    df_ano["aprov"] = round((3*df_ano["V"] + df_ano["E"]) / (3*df_ano["Total"])*100,2)
    df_ano = df_ano.reset_index()
    df_ano.columns.name = None
    df_ano = df_ano[["ano", "Total", "V", "E", "D", "aprov"]]
    df_ano = df_ano.sort_values(by="Total", ascending=False)
    df_ano.index = range(1, len(df_ano) + 1)

    df_dia= pd.DataFrame(data_jogos)
    df_dia = df_dia[["dia", "resultado"]]
    df_dia = df_dia.groupby("dia")["resultado"].value_counts().unstack(fill_value=0)
    df_dia["Total"] = df_dia.sum(axis=1)
    df_dia["Aprov"] = round((3*df_dia["V"] + df_dia["E"]) / (3*df_dia["Total"])*100,2)
    df_dia = df_dia.reset_index()
    df_dia.columns.name = None
    df_dia = df_dia[["dia", "Total", "V", "E", "D", "Aprov"]]
    df_dia = df_dia.sort_values(by="Total", ascending=False)
    df_dia.index = range(1, len(df_dia) + 1)

    
    df_dia_semana= pd.DataFrame(data_jogos)
    df_dia_semana = df_dia_semana[["dia_da_semana", "resultado"]]
    df_dia_semana['dia_da_semana'] = df_dia_semana['dia_da_semana'].astype(int).map(dias_map)
    df_dia_semana = df_dia_semana.groupby("dia_da_semana")["resultado"].value_counts().unstack(fill_value=0)
    df_dia_semana["Total"] = df_dia_semana.sum(axis=1)
    df_dia_semana["Aprov"] = round((3*df_dia_semana["V"] + df_dia_semana["E"]) / (3*df_dia_semana["Total"])*100,2)
    df_dia_semana = df_dia_semana.reset_index()
    df_dia_semana.columns.name = None
    df_dia_semana = df_dia_semana[["dia_da_semana", "Total", "V", "E", "D", "Aprov"]]
    df_dia_semana = df_dia_semana.sort_values(by="Total", ascending=False)
    df_dia_semana.index = range(1, len(df_dia_semana) + 1)

    context = {'df_mes': df_mes.to_dict(orient='records'),
               'df_ano': df_ano.to_dict(orient='records'),
               'df_dia': df_dia.to_dict(orient='records'),
               'df_dia_semana': df_dia_semana.to_dict(orient='records')}
    return render(request, 'meus_jogos_app/estatisticas_datas.html', context)

def gera_df(request):
    jogos = Jogo.objects.all()
    adversarios = Jogo.objects.values_list('adversario', flat=True).distinct()
    arbitro = Jogo.objects.values_list('arbitro', flat=True).distinct()
    estadios =Jogo.objects.values_list('estadio', flat=True).distinct()
    locais = Jogo.objects.values_list('local_estadio', flat=True).distinct()
    locais_adv = Jogo.objects.values_list('local_adv', flat=True).distinct()
    campeonatos = Jogo.objects.values_list('campeonato', flat=True).distinct()
    autores_gol = Jogador.objects.values_list('jogador', flat=True).distinct()
    placar = [f"{gols_flu} x {gols_adv}" for gols_flu, gols_adv in Jogo.objects.values_list('gols_flu', 'gols_adv').distinct()]

    jogadores_queryset = Jogador.objects.all()

    # Filtre técnicos e jogadores a partir do queryset original
    tecnicos = jogadores_queryset.filter(jogador__icontains='TEC').values_list('jogador', flat=True).distinct()
    jogadores = jogadores_queryset.exclude(jogador__icontains='TEC').values_list('jogador', flat=True).distinct()

    # Assistentes
    assistentes = jogadores_queryset.values_list('jogador', flat=True).distinct()
    resultados = ['V', 'E', 'D']  # Vitória, Empate, Derrota

    # Função para tratar os filtros que vêm como JSON
    def tratar_filtro_json(filtro):
        if filtro:
            try:
                filtro_list = json.loads(filtro)  # Converte a string JSON para um objeto Python
                return [item['value'] for item in filtro_list]  # Extrai os valores da chave 'value'
            except json.JSONDecodeError:
                return []  # Se não for um JSON válido, retorna uma lista vazia
        return []

    # Captura os filtros do GET
    dia = request.GET.get('dia')
    mes = request.GET.get('mes')
    ano = request.GET.get('ano')
    adversario = request.GET.get('adversario')
    estadio = request.GET.get('estadio')
    local_jogo = request.GET.get('local_jogo')
    local_adversario = request.GET.get('local_adversario')
    campeonato = request.GET.get('campeonato')
    resultado = request.GET.get('resultado')
    placar = request.GET.get('placar')
    publico = request.GET.get('publico')
    jogador = request.GET.get('jogador')
    tecnico = request.GET.get('tecnico')
    autor_gol = request.GET.get('autor_gol')
    assistente = request.GET.get('assistente')
    dupla_gol = request.GET.get('dupla_gol')
    dupla_assistencia = request.GET.get('dupla_assistencia')

    # Trata os filtros que podem ser passados como JSON
    dia_values = tratar_filtro_json(dia)
    mes_values = tratar_filtro_json(mes)
    ano_values = tratar_filtro_json(ano)
    adversario_values = tratar_filtro_json(adversario)
    estadio_values = tratar_filtro_json(estadio)
    local_jogo_values = tratar_filtro_json(local_jogo)
    local_adversario_values = tratar_filtro_json(local_adversario)
    campeonato_values = tratar_filtro_json(campeonato)
    resultado_values = tratar_filtro_json(resultado)
    placar_values = tratar_filtro_json(placar)
    jogador_values = tratar_filtro_json(jogador)
    tecnico_values = tratar_filtro_json(tecnico)
    autor_gol_values = tratar_filtro_json(autor_gol)
    assistente_values = tratar_filtro_json(assistente)
    dupla_gol_values = tratar_filtro_json(dupla_gol)
    dupla_assistencia_values = tratar_filtro_json(dupla_assistencia)

    # Filtros de data (com tratamento para listas JSON)
    if dia_values:
        jogos = jogos.filter(data__day__in=dia_values)
    if mes_values:
        jogos = jogos.filter(data__month__in=mes_values)
    if ano_values:
        jogos = jogos.filter(data__year__in=ano_values)

    # Filtros gerais
    if adversario_values:
        jogos = jogos.filter(adversario__in=adversario_values)
    if estadio_values:
        jogos = jogos.filter(estadio__in=estadio_values)
    if local_jogo_values:
        jogos = jogos.filter(local_jogo__in=local_jogo_values)
    if local_adversario_values:
        jogos = jogos.filter(local_adversario__in=local_adversario_values)
    if campeonato_values:
        jogos = jogos.filter(campeonato__in=campeonato_values)
    if resultado_values:
        map_resultados = {
            'Vitória': 'V',
            'Derrota': 'D',
            'Empate': 'E'
        }
        resultado_values = [map_resultados.get(resultado, resultado) for resultado in resultado_values]
        jogos = jogos.filter(resultado__in=resultado_values)
    if placar_values:
        jogos = jogos.filter(placar__in=placar_values)
    if publico:
        jogos = jogos.filter(publico__gte=publico)
    if tecnico_values:
        jogos = jogos.filter(tecnico__in=tecnico_values)

    # Filtros relacionados a jogadores
    if autor_gol_values:
        jogos = jogos.filter(gols__autor_gol__in=autor_gol_values).distinct()

        # Jogador (autor ou assistente)
    if jogador_values:
        for jogador in jogador_values:
            jogos = jogos.filter(escalacao__jogador=jogador)

    # Assistente
    if assistente_values:
        jogos = jogos.filter(gols__assistencia__in=assistente_values).distinct()

    # Dupla Gol e Assistência
    if dupla_gol_values and dupla_assistencia_values:
        jogos = jogos.filter(
            Q(gols__autor_gol__in=dupla_gol_values) &
            Q(gols__assistencia__in=dupla_assistencia_values)
        ).distinct()


    data = {
        "id": [jogo.id for jogo in jogos],
        "fluminense": "Fluminense",  # Nome do time (fixo, já que não muda)
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
            ]) for jogo in jogos
        ]
    }

    # Criar o DataFrame
    df_jogos = pd.DataFrame(data)

    # Formatar o público com vírgula como separador de milhar
    df_jogos['publico'] = df_jogos['publico'].apply(lambda x: f"{x:,}".replace(",", "."))

    # Definir as colunas do DataFrame com os nomes desejados
    df_jogos.columns = ["ID", "Fluminense", "Placar", "Adversário", "Estádio", "Data", "Campeonato", "Árbitro", "Público", "Gols"]

    # Organizar as colunas na ordem desejada
    df_jogos = df_jogos[["ID", "Fluminense", "Placar", "Adversário", "Estádio", "Data", "Campeonato", "Público", "Gols"]]

    # Ordenar os jogos por ID em ordem decrescente
    df_jogos = df_jogos.sort_values(by="ID", ascending=False)

    # Converter para HTML
    df_html = df_jogos.to_html(index=False, classes='table table-striped') if not df_jogos.empty else "<p>⚠️ Nenhum jogo encontrado.</p>"

    # Contexto para o template
    context = {
        'df_html': df_html,
        'placares': placar,
        'arbitros': arbitro,
        'adversarios': adversarios,
        'estadios': estadios,
        'local_estadio': locais,
        'local_adv': locais_adv,
        'campeonatos': campeonatos,
        'autores_gol': autores_gol,
        'jogadores': jogadores,
        'tecnicos': tecnicos,
        'assistentes': assistentes,
        'resultados': resultados,
    }

    return context
    
def personalizar(request):
    
    context = gera_df(request)

    return render(request, 'meus_jogos_app/personalizar.html', context)

def exibir_df(request):
    
    context = gera_df(request)

    return render(request, 'meus_jogos_app/exibir_resultado.html.html', context)
