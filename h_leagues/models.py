from django.db import models

'''
You can change the leagues names here
'''
LEAGUES = (
    ('OHL', 'Ontario Hockey League'),
    ('QMJHL', 'Quebec Major Junior Hockey League'),
    ('WHL', 'Western Hockey League'),
)

PO_MARKS = (
    ('x - ', 'Clinched Playoff Spot'),
    ('y - ', 'Division Champion'),
    ('z - ', 'Conference Champion'),
    ('', '')
)

RESULTADOS = (
    ('', ''),
    ('f', 'FINAL'),
    ('ot', 'FINAL-OT'),
    ('so', 'FINAL-SO'),
)

class League(models.Model):
    name= models.CharField(max_length=5, primary_key=True,choices=LEAGUES)
    rs_games = models.IntegerField(default=1)
    season = models.CharField(default='')
    color = models.CharField(default='')
    bg_color = models.CharField(default='')

class Conference(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    non_division = models.IntegerField(default=0)

class Division(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    po_tops = models.IntegerField(default=1)

class Team(models.Model):
    city = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    abr = models.CharField(max_length=5, primary_key=True)
    # league = models.CharField(max_length=5, choices=LEAGUES)
    # conference = models.CharField(max_length=30, default='')
    division = models.CharField(max_length=30, default='')
    holder = models.BooleanField(default=False) # title holder

    def __str__(self):
        return "%s %s" % (self.city, self.name)

class RS_clubs(models.Model):
    eq = models.ForeignKey(Team, on_delete=models.CASCADE)
    seed = models.IntegerField(default=1)
    p_seed = models.IntegerField(default=1)
    po_marks = models.CharField(default='', choices=PO_MARKS) # title holder
    pts = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    otl = models.IntegerField(default=0)
    sol = models.IntegerField(default=0)
    gf = models.IntegerField(default=0)
    ga = models.IntegerField(default=0)
    diff = models.IntegerField(default=0)
    streak = models.CharField(max_length=3, default='W 0')
    games = models.ManyToManyField("self", through='Match', through_fields=('home', 'away'))

    def __init__(self, team):
        self.eq = team
        self.save()

    def __lt__(self, other):
        if self.pts != other.pts:
            return self.pts > other.pts
        elif self.diff != other.diff:
            return self.diff > other.diff
        elif self.gf != other.gf:
            return self.gf > other.gf
        elif self.eq.city != other.eq.city:
            return  self.eq.city < other.eq.city

    def seq(self, result):
        r = (self.streak).split(" ")
        if result == r[0]:
            s = int(r[1]) + 1
            self.streak = "%s %d" % (r[0], s)
            self.save()
        else:
            self.streak = "%s 1" % result
            self.save()

    def games(self):
        return self.wins + self.loss + self.otl + self.sol

    def pct(self):
        jogos = self.games()
        if jogos == 0:
            return '0.000'
        else:
            return '%05.3f' % (self.pts/(jogos*2))


class Series(models.Model):
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
    away = models.ForeignKey(RS_clubs, on_delete=models.CASCADE)
    a_score = models.IntegerField(default=0)
    home = models.ForeignKey(RS_clubs, on_delete=models.CASCADE)
    h_score = models.IntegerField(default=0)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    resultado = models.CharField(max_length=2, choices=RESULTADOS, default='')
    winner = models.CharField(max_length=50, default='')

    # def __init__(self):

    def __lt__(self, other):
        return self.pk > other.pk

# Create your models here.
# from h_leagues.models import *
# a = Team.objects.filter(league='OHL')
