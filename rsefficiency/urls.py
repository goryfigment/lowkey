from django.conf.urls import url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from rsefficiency.controllers import site

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', site.main, name='site'),

    url(r'^treasure_trails/$', site.treasure_trails, name='treasure_trails'),
    url(r'^treasure_trails/(\d+)/$', csrf_exempt(site.clue_id_search), name='clue_id_search'),
    url(r'^clue/string_search/$',  csrf_exempt(site.clue_string_search), name='clue_string_search'),
    url(r'^treasure_trails/([a-z]+)/$',  csrf_exempt(site.clue_type_search), name='clue_type_search'),
]
