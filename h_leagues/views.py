from .models import *
import random
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

# Create your views here.
def index(request):
    tt = Team.objects.order_by('pts', 'diff', 'gf', 'city')[:10]
    w = Match.objects.filter(league='WHL').order_by('pk')[:4]
    o = Match.objects.filter(league='OHL').order_by('pk')[:4]
    q = Match.objects.filter(league='QMJHL').order_by('pk')[:4]
    return render(request, 'h_leagues/index.html', {'teams': tt, 'whl': w, 'qmjhl': q, 'ohl': o})

def league(request, liga):
    tt = Team.objects.filter(league=liga).order_by('pts', 'diff', 'gf', 'city')
    games = Match.objects.filter(league=liga).order_by('pk')[:8]
    return render(request, 'h_leagues/leagues.html', {'teams': tt, 'gg': games})

def standings(request, liga):
    conf1 = []
    conf2 = []
    if liga == 'QMJHL':
        div1 = Team.objects.filter(league=liga, division='West').order_by('pts', 'diff', 'gf', 'city')
        div2 = Team.objects.filter(league=liga, division='East').order_by('pts', 'diff', 'gf', 'city')
        div3 = Team.objects.filter(league=liga, division='Maritimes').order_by('pts', 'diff', 'gf', 'city')
        lideres = [div1[0], div2[0], div3[0]]
        rest = []
        for i in range(1,6):
            rest.append(div1[i])
            rest.append(div2[i])
            rest.append(div3[i])
        lideres.sort()
        rest.sort()
        for t in lideres:
            conf1.append(t)
        for t in rest:
            conf1.append(t)
        return render(request, 'h_leagues/standings.html',
                      {'q_west': div1, 'q_east': div2, 'q_marit': div3, 'total': conf1, 'league': liga})
    elif liga == 'OHL':
        div1 = Team.objects.filter(league=liga, division='East', conference='Eastern').order_by('pts', 'diff', 'gf', 'city')
        div2 = Team.objects.filter(league=liga, division='Central', conference='Eastern').order_by('pts', 'diff', 'gf', 'city')
        div3 = Team.objects.filter(league=liga, division='Midwest', conference='Western').order_by('pts', 'diff', 'gf', 'city')
        div4 = Team.objects.filter(league=liga, division='West', conference='Western').order_by('pts', 'diff', 'gf', 'city')
        el = [div1[0], div2[0]]
        wl = [div3[0], div4[0]]
        er = []
        wr = []
        for i in range(1,5):
            er.append(div1[i])
            er.append(div2[i])
            wr.append(div3[i])
            wr.append(div4[i])
        el.sort()
        er.sort()
        wl.sort()
        wr.sort()
        for t in el:
            conf1.append(t)
        for t in wl:
            conf2.append(t)
        for t in er:
            conf1.append(t)
        for t in wr:
            conf2.append(t)
        return render(request, 'h_leagues/standings.html',
                          {'o_central': div2, 'o_east': div1, 'o_midwest': div3,
                           'o_west': div4, 'EC': conf1, 'WC': conf2, 'league': liga})
    else:
        # ---- WHL ----
        div1 = Team.objects.filter(league=liga, division='East', conference='Eastern').order_by('pts', 'diff', 'gf', 'city')
        div2 = Team.objects.filter(league=liga, division='Central', conference='Eastern').order_by('pts', 'diff', 'gf', 'city')
        div3 = Team.objects.filter(league=liga, division='B.C.', conference='Western').order_by('pts', 'diff', 'gf', 'city')
        div4 = Team.objects.filter(league=liga, division='U.S.', conference='Western').order_by('pts', 'diff', 'gf', 'city')
        for wc in range(3,6):
            conf1.append(div1[wc])
            conf1.append(div2[wc])
        for wc in range(3,5):
            conf2.append(div3[wc])
            conf2.append(div4[wc])
        conf1.sort()
        conf2.sort()
        return render(request, 'h_leagues/standings.html', {'w_central': div2[:3], 'w_east': div1[:3], 'bc': div3[:3],
                       'us': div4[:3], 'e_wc': conf1, 'w_wc': conf2, 'league': liga})

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
    not_played = Match.objects.filter(league=liga, resultado='').order_by('pk')
    played = Match.objects.filter(league=liga, resultado=('f', 'ot', 'so')).order_by('pk')
    # po = [] # postseason
    return render(request, 'h_leagues/schedule.html', {'P': played, 'nP': not_played})

def simulation(request, match_id):
    partida = Match.objects.get(pk=match_id)
    home = Team.objects.filter(abr=partida.home)
    away = Team.objects.filter(abr=partida.away)
    if not partida.resultado:
        h = random.randint(0, 6)
        a = random.randint(0, 6)
        if h == a:
            if (random.uniform(0.00, 0.99) < 0.25):
                partida.resultado = 'so'
            else:
                partida.resultado = 'ot'
            if (random.uniform(0.00, 0.99) < 0.60):
                h += 1
                home.wins += 1
                if partida.resultado == 'so':
                    away.sol += 1
                else:
                    away.otl += 1
            else:
                a += 1
                away.wins += 1
                if partida.resultado == 'so':
                    home.sol += 1
                else:
                    home.otl += 1
        else:
            partida.resultado = 'f'
            if h > a:
                home.wins += 1
                away.loss += 1
            else:
                home.wins += 1
                away.loss += 1
        partida.h_score += h
        partida.a_score += a
        home.gf += h
        home.ga += a
        away.gf += a
        away.gf += h
        home.save()
        away.save()
        partida.save()
    return render(request, 'h_leagues/match.html', {'partida': partida, 'casa': home, 'fora': away})
