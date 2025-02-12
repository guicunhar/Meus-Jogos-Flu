import csv
import requests
from datetime import datetime
from io import StringIO
from django.core.management.base import BaseCommand
from meus_jogos_app.models import Jogo, Jogador, Gol, Escalacao
import subprocess
import sys

class Command(BaseCommand):
    help = 'Importa dados de arquivos CSV para as tabelas do banco de dados'

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.HTTP_INFO(f'IMPORTANDO DADOS...'))

        # Caminhos dos arquivos CSV - ajuste para os seus locais
        jogos_csv = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRFp3ZZZFagId4GnO00-LBfxWy9T5D5yo279D4W--5-NheEj8Txh3UV98NCCHljGAHEFYZ1bKxSDxBG/pub?output=csv'
        gols_csv = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRFp3ZZZFagId4GnO00-LBfxWy9T5D5yo279D4W--5-NheEj8Txh3UV98NCCHljGAHEFYZ1bKxSDxBG/pub?gid=885969783&single=true&output=csv'
        escalacoes_csv = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRFp3ZZZFagId4GnO00-LBfxWy9T5D5yo279D4W--5-NheEj8Txh3UV98NCCHljGAHEFYZ1bKxSDxBG/pub?gid=2101258360&single=true&output=csv'
        jogadores_csv = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRFp3ZZZFagId4GnO00-LBfxWy9T5D5yo279D4W--5-NheEj8Txh3UV98NCCHljGAHEFYZ1bKxSDxBG/pub?gid=601199534&single=true&output=csv'

        # Importa dados dos jogos
        self.importar_jogos(jogos_csv)

        # Importa dados dos jogadores
        self.importar_jogadores(jogadores_csv)

        # Importa dados dos gols
        self.importar_gols(gols_csv)

        # Importa dados das escalações
        self.importar_escalacoes(escalacoes_csv)

        subprocess.run([sys.executable, '-m', 'manage', 'runserver'])


    def importar_jogos(self, arquivo_csv):
        resposta = requests.get(arquivo_csv)
        resposta.raise_for_status()  # Garante que a requisição foi bem-sucedida
        resposta.encoding = 'utf-8'

        # Lê o CSV a partir da resposta
        csvfile = StringIO(resposta.text)
        leitor = csv.DictReader(csvfile)
        for row in leitor:
            gols_flu = int(row['gols_flu'])  # Converta os valores para inteiros
            gols_adv = int(row['gols_adv'])  # Converta os valores para inteiros

            # Atribuindo o valor de 'resultado' com base na comparação
            if gols_flu > gols_adv:
                resultado = 'V'  # Vitória
            elif gols_flu < gols_adv:
                resultado = 'D'  # Derrota
            else:
                resultado = 'E'  # Empate

            # Converte a data para o formato correto (YYYY-MM-DD)
            data_str = row['data']
            try:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                data_formatada = data_obj.strftime("%Y-%m-%d")
            except ValueError:
                self.stdout.write(self.style.ERROR(f"Erro ao processar a data {data_str}. Formato incorreto."))
                continue


            # Agora cria ou atualiza o registro de jogo
            Jogo.objects.update_or_create(
                id=row['id_jogo'],
                defaults={
                    'gols_flu': gols_flu,
                    'gols_adv': gols_adv,
                    'adversario': row['adversario'],
                    'local_adv': row['local_adv'],
                    'estadio': row['estadio'],
                    'local_estadio': row['local_estadio'],
                    'data': data_formatada,
                    'resultado': resultado,  # Atribui o resultado calculado
                    'campeonato': row['campeonato'],
                    'arbitro': row['arbitro'],
                    'publico': row['publico']
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Dados dos jogos importados com sucesso!'))

    def importar_gols(self, arquivo_csv):
        resposta = requests.get(arquivo_csv)
        resposta.raise_for_status()  # Garante que a requisição foi bem-sucedida
        resposta.encoding = 'utf-8'

        csvfile = StringIO(resposta.text)
        leitor = csv.DictReader(csvfile)
        for row in leitor:
            jogo = Jogo.objects.get(id=row['id_jogo'])
            autor = Jogador.objects.get(id_jogador=row['id_autor'])
            assistente = Jogador.objects.get(id_jogador=row['id_ass']) if row['id_ass'] else None

            Gol.objects.update_or_create(
                id_jogo=jogo,
                id_autor=autor,
                id_ass=assistente,
                autor_gol=row['autor_gol'],
                assistencia=row['assistencia']
            )
        self.stdout.write(self.style.SUCCESS(f'Dados dos gols importados com sucesso!'))

    def importar_escalacoes(self, arquivo_csv):
        resposta = requests.get(arquivo_csv)
        resposta.raise_for_status()
        resposta.encoding = 'utf-8'

        csvfile = StringIO(resposta.text)
        leitor = csv.DictReader(csvfile)
        for row in leitor:
            jogo = Jogo.objects.get(id=row['id_jogo'])
            jogador = Jogador.objects.get(id_jogador=row['id_jogador'])

            Escalacao.objects.update_or_create(
                id_jogo=jogo,
                id_jogador=jogador,
                defaults={'jogador': row['jogador']}
            )
        self.stdout.write(self.style.SUCCESS(f'Dados das escalações importados com sucesso!'))

    def importar_jogadores(self, arquivo_csv):
        resposta = requests.get(arquivo_csv)
        resposta.raise_for_status()  # Garante que a requisição foi bem-sucedida
        resposta.encoding = 'utf-8'

        csvfile = StringIO(resposta.text)
        leitor = csv.DictReader(csvfile)
        Jogador.objects.update_or_create(
                id_jogador=0,
                defaults={'jogador': "Gol Contra"}
            )
        for row in leitor:
            Jogador.objects.update_or_create(
                id_jogador=row['id_jogador'],
                defaults={'jogador': row['jogador']}
            )
        self.stdout.write(self.style.SUCCESS(f'Dados dos jogadores importados com sucesso!'))
