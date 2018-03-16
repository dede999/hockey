from django.urls import path

from . import views

app_name = 'leagues'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:liga>/', views.league, name='liga'),
    path('<str:liga>/standings', views.standings, name='standings'),
    path('<str:liga>/postseason', views.playoffs, name='postseason'),
    path('<str:liga>/schedule', views.schedule, name='schedule'),
    path('<int:match_id/simulation>', views.simulation, name='simulation')
]