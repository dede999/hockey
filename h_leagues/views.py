from .models import *
import numpy as np
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

#helpers
def get_all():
    return League.objects.all()

def matches(league):
    not_played = Match.objects.filter(league=league, result='').order_by('pk')[:12]
    played = []
    for m in Match.objects.filter(league=league, result='f'):
        played.append(m)
    for m in Match.objects.filter(league=league, result='ot'):
        played.append(m)
    for m in Match.objects.filter(league=league, result='so'):
        played.append(m)
    played.sort()
    return played[:12], not_played

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
    l = League.objects.get(name=liga)
    # po = [] # postseason
    return render(request, 'h_leagues/schedule.html',
                  {'P': played, 'nP': not_played,
                   'l': l, 'll': get_all()})

def simulation(request, match_id):
    partida = Match.objects.get(pk=match_id)
    l = League.objects.get(name=partida.league)
    home = RS_clubs.objects.get(id=partida.home_id)
    away = RS_clubs.objects.get(id=partida.away_id)
    played, not_played = matches(partida.league)
    regulation = False
    for per in range(4):
        for turn in range(3):
            # home attack
            attack = home
            defense =  away
            am = int((attack.off_power + 2*attack.momentum)/3) # attacking momentum
            dm = int((defense.def_power + 2*defense.momentum)/3) # defending momentum
            if np.random.randint(0,am+dm) <= am:
                # goal
                attack.momentum += 50
                defense.momentum -= 50
                partida.h_score += 1
                attack.gf += 1
                defense.ga += 1
                if per == 3:
                    break
            else:
                # no goal
                attack.momentum -= 30
                defense.momentum += 30
            # visitors attack
            attack = away
            defense =  home
            am = int((attack.off_power + 2*attack.momentum)/3) # attacking momentum
            dm = int((defense.def_power + 2*defense.momentum)/3) # defending momentum
            if np.random.randint(0,am+dm) <= am:
                # goal
                attack.momentum += 50
                defense.momentum -= 50
                partida.h_score += 1
                attack.gf += 1
                defense.ga += 1
                if per == 3:
                    break
            else:
                # no goal
                attack.momentum -= 30
                defense.momentum += 30
        if per == 2 and partida.h_score != partida.a_score:
            # match over in regulation
            partida.result = 'f'
            if partida.h_score > partida.a_score:
                winner = home
                loser = away
            else:
                winner = away
                loser = home
            winner.wins += 1
            winner.seq('W')
            winner.l5('W')
            winner.pts += 2
            loser.loss += 1
            loser.seq('L')
            loser.l5('L')
            regulation = True
            break
    if partida.h_score != partida.a_score:
        if not regulation:
            # overtime
            partida.result = 'ot'
            if partida.h_score > partida.a_score:
                winner = home
                loser = away
            else:
                winner = away
                loser = home
            winner.wins += 1
            winner.seq('W')
            winner.l5('W')
            winner.pts += 2
            loser.otl += 1
            loser.pts += 1
            loser.seq('OTL')
            loser.l5('OTL')
    else:
        # PSO
        partida.result = 'so'
        hm = home.off_power + home.momentum
        am = away.off_power + away.momentum
        if np.random.randint(0, hm+am) < hm:
            winner = home
            loser = away
        else:
            winner = away
            loser = home
        winner.wins += 1
        winner.gf += 1
        winner.pts += 2
        winner.seq('W')
        winner.l5('W')
        loser.sol += 1
        loser.ga += 1
        loser.seq('SOL')
        loser.l5('SOL')
    partida.save()
    message = '%s %d @ %s %d' % (away.t_abr.name, partida.a_score, home.t_abr.name, partida.h_score)
    return render(request, 'h_leagues/schedule.html',
                  {'P': played, 'nP': not_played, 'msg': message,
                   'result': partida.get_result_display(), 'l': l, 'll': get_all()})

# from h_leagues.models import *
# m = Match.objects.first
# h = Team.objects.filter(abr=m.home)[0]
