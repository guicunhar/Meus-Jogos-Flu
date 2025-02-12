from django.db import models

class Jogo(models.Model):
    gols_flu = models.IntegerField()
    gols_adv = models.IntegerField()
    adversario = models.CharField(max_length=100)
    local_adv = models.CharField(max_length=3)
    estadio = models.CharField(max_length=100)
    local_estadio = models.CharField(max_length=3)
    data = models.DateField()
    resultado = models.CharField(max_length=5)
    campeonato = models.CharField(max_length=100)
    arbitro = models.CharField(max_length=100)
    publico = models.IntegerField()

    def __str__(self):
        return f"{self.adversario} ({self.data})"

class Jogador(models.Model):
    id_jogador = models.AutoField(primary_key=True)
    jogador = models.CharField(max_length=100)

    def __str__(self):
        return self.jogador

class Gol(models.Model):
    id_jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name="gols")
    id_autor = models.ForeignKey(Jogador, on_delete=models.CASCADE, related_name="autor_gol")
    autor_gol = models.CharField(max_length=100)    
    id_ass = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name="autor_assist")
    assistencia = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Gol de {self.autor_gol} no jogo {self.id_jogo}"


class Escalacao(models.Model):
    id_jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE)
    id_jogador = models.ForeignKey(Jogador, on_delete=models.CASCADE)
    jogador = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.jogador} - {self.id_jogo}"
