from django.conf.urls import patterns, include, url
from django.contrib import admin

from games import urls as games_urls

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include(games_urls)),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^admin/', include(admin.site.urls)),
)

