from .models import *
import random
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

#helpers
def get_all():
    return League.objects.all()

def matches(league):
    not_played = Match.objects.filter(league=league, resultado='').order_by('pk')
    played = []
    for m in Match.objects.filter(league=league, resultado='f'):
        played.append(m)
    for m in Match.objects.filter(league=league, resultado='ot'):
        played.append(m)
    for m in Match.objects.filter(league=league, resultado='so'):
        played.append(m)
    played.sort()
    return played, not_played


# Create your views here.
def index(request):
    s = Season.objects.all().last()
    qw = Winners.objects.get(season=s.final-1, league='QMJHL')
    ow = Winners.objects.get(season=s.final-1, league='OHL')
    ww = Winners.objects.get(season=s.final-1, league='WHL')
    title = Winners.objects.get(season=s.final-1, league='MMC')
    tt = Team.objects.order_by(
        '-mmc_championship', '-l_championship', 'city')[:5]
    ll = get_all()
    # tt = Team.objects.order_by('-pts', '-diff', '-gf', 'city')[:15]
    return render(request, 'h_leagues/index.html',
                  {'teams': tt, 'past': s, 'ohl': ow,
                   'qhl': qw, 'whl': ww, 'mmc': title, 'll': ll})

def league(request, liga):
    s = Season.objects.all().last()
    league = League.objects.get(name=liga)
    champ = Winners.objects.filter(league=liga, season=s.final-1)
    tt = RS_clubs.objects.filter(l_name=liga).order_by('-pts', '-diff', '-gf', 't_abr__city')
    games = Match.objects.filter(league=liga).order_by('pk')[:6]
    ll = get_all()
    return render(request, 'h_leagues/leagues.html',
                  {'teams': tt, 'gg': games,
                   'winner': champ, 'l': league, 'll': ll})

def standings(request, liga):
    # temp = Season.objects.last()
    l = League.objects.get(name=liga)
    tps = l.conference_set.first().division_set.count() * l.conference_set.first().division_set.first().tops
    total = tps + l.conference_set.first().wild_card
    ll = get_all()
    return render(request, 'h_leagues/standings.html',
                  {'l': l, 'tops': tps, 'poff': total, 'll': ll})

def playoffs(request, liga):
    if liga == 'QMJHL':
        r1 = POseries.objects.filter(league=liga, series='First Round')
        r2 = POseries.objects.filter(league=liga, series='Second Round')
        r3 = POseries.objects.filter(league=liga, series='Semifinal')
        r4 = POseries.objects.filter(league=liga, series='Final')
        return render(request, 'h_leagues/postseason.html', {'liga': liga, 'r1': r1, 'r2': r2, 'r3': r3, 'r4': r4})
    elif liga == 'WHL':
        r1e = POseries.objects.filter(league=liga, series='Division SF', conference='Eastern')
        r1w = POseries.objects.filter(league=liga, series='Division SF', conference='Western')
        r2e = POseries.objects.filter(league=liga, series='Division Final', conference='Eastern')
        r2w = POseries.objects.filter(league=liga, series='Division Final', conference='Western')
        r3e = POseries.objects.filter(league=liga, series='Conference Final', conference='Eastern')
        r3w = POseries.objects.filter(league=liga, series='Conference Final', conference='Western')
        r4 = POseries.objects.filter(league=liga, series='Final')
        return render(request, 'h_leagues/postseason.html',
                      {'liga': liga, 'r1e': r1e, 'r1w': r1w, 'r2e': r2e, 'r2w': r2w, 'r3e': r3e, 'r3w': r3w, 'r4': r4})
    else:
        r1e = POseries.objects.filter(league=liga, series='Eastern R1', conference='Eastern')
        r1w = POseries.objects.filter(league=liga, series='Western R1', conference='Western')
        r2e = POseries.objects.filter(league=liga, series='Eastern R2', conference='Eastern')
        r2w = POseries.objects.filter(league=liga, series='Western R2', conference='Western')
        r3e = POseries.objects.filter(league=liga, series='Conference F', conference='Eastern')
        r3w = POseries.objects.filter(league=liga, series='Conference F', conference='Western')
        r4 = POseries.objects.filter(league=liga, series='Final')
        return render(request, 'h_leagues/postseason.html',
                      {'liga': liga, 'r1e': r1e, 'r1w': r1w, 'r2e': r2e, 'r2w': r2w, 'r3e': r3e, 'r3w': r3w, 'r4': r4})


def schedule(request, liga):
    played, not_played = matches(liga)
    # po = [] # postseason
    return render(request, 'h_leagues/schedule.html', {'P': played, 'nP': not_played})

def simulation(request, match_id):
    partida = Match.objects.get(pk=match_id)
    home = Team.objects.filter(abr=partida.home)[0]
    away = Team.objects.filter(abr=partida.away)[0]
    played, not_played = matches(partida.league)
    if not partida.resultado:
        h = random.randint(0, 5)
        a = random.randint(0, 5)
        if h == a: # overtime
            if (random.uniform(0.00, 0.99) < 0.35):
                partida.resultado = 'so'
            else:
                partida.resultado = 'ot'
            if (random.uniform(0.00, 0.99) < 0.60):
                h += 1
                home.seq("W")
                partida.winner = partida.home
                win = home
                home.wins += 1
                home.pts += 2
                away.pts += 1
                if partida.resultado == 'so':
                    away.sol += 1
                    away.seq("SOL")
                else:
                    away.otl += 1
                    away.seq("OTL")
            else:
                a += 1
                partida.winner = partida.away
                win = away
                away.seq("W")
                away.wins += 1
                away.pts += 2
                home.pts += 1
                if partida.resultado == 'so':
                    home.sol += 1
                    home.seq("SOL")
                else:
                    home.otl += 1
                    home.seq("OTL")
        else:
            partida.resultado = 'f'
            if h > a:
                partida.winner = partida.home
                win = home
                home.wins += 1
                away.loss += 1
                home.pts += 2
                home.seq("W")
                away.seq("L")
            else:
                partida.winner = partida.away
                win = away
                away.wins += 1
                home.loss += 1
                away.pts += 2
                away.seq("W")
                home.seq("L")
        partida.h_score = h
        partida.a_score = a
        home.gf += h
        home.ga += a
        away.gf += a
        away.ga += h
        home.diff = home.gf - home.ga
        away.diff = away.gf - away.ga
        home.save()
        away.save()
        partida.save()
    message = '%s %d @ %s %d' % (away.name, partida.a_score, home.name, partida.h_score)
    return render(request, 'h_leagues/schedule.html',
                  {'P': played, 'nP': not_played, 'msg': message, 'result': partida.get_resultado_display()})

# from h_leagues.models import *
# m = Match.objects.first
# h = Team.objects.filter(abr=m.home)[0]
# git commit -m "Simulations now work, and so standings. Improvements on the templates"