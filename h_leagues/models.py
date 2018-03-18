from django.db import models

'''
You can change the leagues names here
'''
LEAGUES = (
    ('OHL', 'Ontario Hockey League'),
    ('QMJHL', 'Quebec Major Junior Hockey League'),
    ('WHL', 'Western Hockey League'),
)

RESULTADOS = (
    ('', ''),
    ('f', 'FINAL'),
    ('ot', 'FINAL-OT'),
    ('so', 'FINAL-SO'),
)

class Team(models.Model):
    city = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    abr = models.CharField(max_length=5)
    league = models.CharField(max_length=5, choices=LEAGUES)
    conference = models.CharField(max_length=30, default='')
    division = models.CharField(max_length=30, default='')
    pts = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    otl = models.IntegerField(default=0)
    sol = models.IntegerField(default=0)
    gf = models.IntegerField(default=0)
    ga = models.IntegerField(default=0)
    diff = models.IntegerField(default=0)
    streak = models.CharField(max_length=3, default='W0')

    def __str__(self):
        return "%s %s" % (self.city, self.name)

    def __lt__(self, other):
        if self.pts != other.pts:
            return self.pts > other.pts
        elif self.diff != other.diff:
            return self.diff > other.diff
        elif self.gf != other.gf:
            return self.gf < other.gf
        elif self.city != other.city:
            return  self.city < other.city

    def games(self):
        return self.wins + self.loss + self.otl + self.sol

    def pct(self):
        jogos = self.games()
        if jogos == 0:
            return '0.000'
        else:
            return '%05.3f' % (self.pts/(jogos*2))


class POseries(models.Model):
    high = models.CharField(max_length=100, default='')
    h_msg = models.CharField(max_length=100, default='')
    h_wins = models.IntegerField(default=0)
    low = models.CharField(max_length=100, default='')
    l_msg = models.CharField(max_length=100, default='')
    l_wins = models.IntegerField(default=0)
    series = models.CharField(max_length=150)
    conference = models.CharField(max_length=30, default='')
    league = models.CharField(max_length=5, choices=LEAGUES)


class Match(models.Model):
    away = models.CharField(max_length=50)
    a_score = models.IntegerField(default=0)
    home = models.CharField(max_length=50)
    h_score = models.IntegerField(default=0)
    league = models.CharField(max_length=5, choices=LEAGUES)
    resultado = models.CharField(max_length=2, choices=RESULTADOS, default='')
    winner = models.CharField(max_length=50, default='')

    def __lt__(self, other):
        return self.pk < other.pk


# Create your models here.
# from h_leagues.models import *
# a = Team.objects.filter(league='OHL')
