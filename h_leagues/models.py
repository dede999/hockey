from django.db import models
import numpy as np

'''
You can change the leagues names here
'''
LEAGUES = (
    ('OHL', 'Ontario Hockey League'),
    ('QMJHL', 'Quebec Major Junior Hockey League'),
    ('WHL', 'Western Hockey League'),
    ('MMC', 'Memorial Cup')
)

PO_MARKS = (
    (1, 'w - '), # Clinched WildCard Spot
    (2, 'x - '), # Clinched Playoff Spot
    (3, 'y - '), # Division Champion
    (4, 'z - '), # Conference Champion
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

    def __str__(self):
        return self.name.upper()

    def get_team(self):
        resp = []
        resp1 = []
        [resp1.append(conf.get_team()) for conf in self.conference_set.all()]
        for line in resp1:
            [resp.append(t) for t in line]
        return resp

    def regular_season(self, season):
        for t in self.get_team():
            rand_off = int(np.random.normal(500, 100))
            rand_def = int(np.random.normal(500, 100))
            RS_clubs(
                t_abr=t, s_year=season, l_name=self,
                off_power=rand_off, def_power=rand_def).save()

    def completeness(self):
        total = self.match_set.count()
        played = total - self.match_set.filter(result='')
        # comp = "%5.2f" % played/total
        return "%d/%d matches (%5.2f %)" % (played, total, (played/total))

class Season(models.Model): #2
    start = models.IntegerField()
    final = models.IntegerField(primary_key=True)
    is_over = models.BooleanField(default=False)

    def __str__(self):
        return "(%d - %d)" % (self.start, self.final)

class Conference(models.Model): #3
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    region = models.CharField(max_length=30)
    wild_card = models.IntegerField(default=0)
    class Meta:
        unique_together = (('league', 'region'))

    def __str__(self):
        return "%s %s Conference" % (self.league, self.region)

    def get_team(self):
        resp = []
        resp1 = []
        [resp1.append(div.get_teams()) for div in self.division_set.all()]
        for line in resp1:
            [resp.append(t) for t in line]
        return resp

    def conf_standings(self):
        tops = []
        wild_c = []
        std = []
        for division in self.division_set.all():
            div = division.div_standings()
            for k in range(division.tops):
                tops.append(div[k])
            for i in range(division.tops,len(div)):
                wild_c.append(div[i])
        tops.sort()
        wild_c.sort()
        [std.append(i) for i in tops]
        [std.append(k) for k in wild_c]
        return  std

class Division(models.Model): #4
    conf = models.ForeignKey(Conference, on_delete=models.CASCADE)
    region = models.CharField(max_length=30)
    tops = models.IntegerField(default=1)
    class Meta:
        unique_together = (('conf', 'region'))

    def __str__(self):
        return "%s %s Division" % (self.conf.league, self.region)

    def get_teams(self):
        resp = []
        [resp.append(t) for t in self.team_set.all()]
        return resp

    def sorted(self):
        vec = []
        [vec.append(rs.rs_clubs_set.last()) for rs in self.get_teams()]
        vec.sort()
        rank = 1
        for rs_clubs in vec:
            rs_clubs.div_placement = rank
            rank += 1
            rs_clubs.save()
        return vec

    def div_standings(self):
        vec = []
        [vec.append(team) for team in self.get_teams()]
        vec.sort()
        return vec

class Team(models.Model): #5
    city = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    abr = models.CharField(max_length=5, primary_key=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    bg_color = models.CharField(max_length=10, default='')
    l_championship = models.IntegerField(default=0)
    mmc_championship = models.IntegerField(default=0)

    def __str__(self):
        return "%s %s" % (self.city, self.name)

    def __lt__(self, other):
        this = self.rs_clubs_set.last()
        that =  other.rs_clubs_set.last()
        return this.div_placement < that.div_placement

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

    def __lt__(self, other):
        if self.pts != other.pts:
            return self.pts > other.pts
        elif self.diff != other.diff:
            return self.diff > other.diff
        elif self.gf != other.gf:
            return self.gf > other.gf
        elif self.t_abr.city != other.t_abr.city:
            return  self.t_abr.city < other.t_abr.city

    def __str__(self):
        return "%s %s" % (self.t_abr, self.s_year)

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

class PostSeason(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    wins = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    end_point = models.CharField(default='', max_length=20)
    participates = models.ManyToManyField('self', through='Series', symmetrical=False)
    class Meta:
        unique_together= (('team', 'season'),)

    def __str__(self):
        return "%s  (%s - %s)" % (self.team, self.wins, self.loss)

class Series(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    phase = models.IntegerField()
    high = models.ForeignKey(PostSeason, on_delete=models.CASCADE, related_name='higher')
    h_wins = models.IntegerField(default=1)
    low = models.ForeignKey(PostSeason, on_delete=models.CASCADE, related_name='lower')
    l_wins = models.IntegerField(default=1)
    conf = models.IntegerField(default=0)
    title = models.CharField(max_length=20, default='')
    class Meta:
        unique_together= (('league', 'season', 'phase', 'high', 'low'),)

    def __str__(self):
        return "#%s%s Rd%d %d" % (self.high,self.low,self.phase,
                self.season.final)

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
        return self.id > other.id

class PSMatch(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
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
    host = models.CharField(max_length=20, default='')

    def champs(self):
        if self.league.name == 'MMC':
            self.champion.mmc_championship += 1
            if self.champion.save():
                print('OK')
        else:
            self.champion.l_championship += 1
            if self.champion.save():
                print('OK')

# Create your models here.
# from h_leagues.models import *
# a = Team.objects.filter(league='OHL')
