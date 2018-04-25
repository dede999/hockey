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
    (1, 'x - '), # Clinched Playoff Spot
    (2, 'y - '), # Division Champion
    (3, 'z - '), # Conference Champion
    (0, '')
)

RESULTADOS = (
    ('', ''),
    ('f', 'FINAL'),
    ('ot', 'FINAL-OT'),
    ('so', 'FINAL-SO'),
)

class League(models.Model): #1
    name= models.CharField(max_length=5, primary_key=True,choices=LEAGUES)
    n_games = models.IntegerField(default=1)
    weeks = models.IntegerField(default=1)
    color = models.CharField(max_length=10, default='')
    bg_color = models.CharField(max_length=10, default='')

class Season(models.Model): #2
    start = models.IntegerField()
    final = models.IntegerField(primary_key=True)
    is_over = models.BooleanField(default=False)

class Conference(models.Model): #3
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    region = models.CharField(max_length=30)
    wild_card = models.IntegerField(default=0)
    class Meta:
        unique_together = (('league', 'region'))

class Division(models.Model): #4
    conf = models.ForeignKey(Conference, on_delete=models.CASCADE)
    region = models.CharField(max_length=30)
    tops = models.IntegerField(default=1)
    class Meta:
        unique_together = (('conf', 'region'))

class Team(models.Model): #5
    city = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    abr = models.CharField(max_length=5, primary_key=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    bg_color = models.CharField(max_length=10, default='')

    def __str__(self):
        return "%s %s" % (self.city, self.name)

class RS_clubs(models.Model): #6
    t_abr = models.ForeignKey(Team, on_delete=models.CASCADE)
    s_year = models.ForeignKey(Season, on_delete=models.CASCADE)
    l_name = models.ForeignKey(League, on_delete=models.CASCADE)
    seed = models.IntegerField(default=1)
    po_marks = models.IntegerField(default=0, choices=PO_MARKS)
    pts = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    otl = models.IntegerField(default=0)
    sol = models.IntegerField(default=0)
    gf = models.IntegerField(default=0)
    ga = models.IntegerField(default=0)
    diff = models.IntegerField(default=0)
    last5 = models.CharField(default=' - - - - ', max_length= 15)
    streak = models.CharField(max_length=3, default='W 0')
    div_placement = models.IntegerField(default=1)
    games = models.ManyToManyField("self", through='Match', through_fields=('home', 'away'))
    off_power = models.IntegerField(default=500)
    momentum = models.IntegerField(default=500)
    def_power = models.IntegerField(default=500)
    class Meta:
        unique_together=(('t_abr', 's_year'), )

    # this class and subsequent methods can be changed according to the sport to be simulated
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
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    phase = models.IntegerField()
    identifier = models.CharField(max_length=2, default='')
    conf = models.IntegerField(default=0)
    title = models.CharField(max_length=20, default='')
    class Meta:
        unique_together= (('league', 'season', 'phase', 'identifier'),)

class PostSeason(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    wins = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    end_point = models.CharField(default='', max_length=20)
    participates = models.ManyToManyField(Series, through='Participation')
    class Meta:
        unique_together= (('team', 'season'),)

class Participation(models.Model):
    team = models.ForeignKey(PostSeason, on_delete=models.CASCADE)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    wins = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    home_adv = models.IntegerField(default=0)
    class Meta:
        unique_together= (('team', 'series'),)


class Match(models.Model):
    away = models.ForeignKey(RS_clubs, on_delete=models.CASCADE, related_name='guest')
    a_score = models.IntegerField(default=0)
    a_rec = models.CharField(max_length=15, default='')
    home = models.ForeignKey(RS_clubs, on_delete=models.CASCADE, related_name='host')
    h_score = models.IntegerField(default=0)
    h_rec = models.CharField(max_length=15, default='')
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    result = models.CharField(max_length=2, choices=RESULTADOS, default='')

    # def __init__(self):

    def __lt__(self, other):
        return self.pk > other.pk

class PSMatch(models.Model):
    season = models.ForeignKey(Series, on_delete=models.CASCADE)
    game = models.IntegerField(default=1)
    h_score = models.IntegerField(default=0)
    a_score = models.IntegerField(default=0)
    result = models.CharField(max_length=15, default='')
    storyline = models.CharField(max_length=40, default='')

class Winners(models.Model):
    champion = models.ForeignKey(Team, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    div_champ = models.BooleanField(default=False)
    division = models.CharField(max_length=10, default='')

# Create your models here.
# from h_leagues.models import *
# a = Team.objects.filter(league='OHL')
