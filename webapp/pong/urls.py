from django.conf.urls import patterns, include, url
from django.contrib import admin

from api import urls as api_urls

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/', include(api_urls)),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^admin/', include(admin.site.urls)),
)

