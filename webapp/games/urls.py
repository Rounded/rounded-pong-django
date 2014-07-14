from django.conf.urls import patterns, url

from games.views import (
    IndexAPIView, GamesAPIView, UsersAPIView, PayDebtAPIView
)

urlpatterns = patterns('',
    url(r'^$', IndexAPIView.as_view(), name='index'),
    url(r'^users/$', UsersAPIView.as_view(), name='users_list'), 
    url(r'^users/(?P<user_id>\d+)/$', UsersAPIView.as_view(), name='users_retrieve'), 
    url(r'^games/$', GamesAPIView.as_view(), name='games_list_create'),
    url(r'^games/(?P<game_id>\d+)/$', GamesAPIView.as_view(), name='games_retrieve'),
    url(r'^pay-debt/$', PayDebtAPIView.as_view(), name='pay_debt'),
)
