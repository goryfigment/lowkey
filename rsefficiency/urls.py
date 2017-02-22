from django.conf.urls import url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from rsefficiency.controllers import site

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', site.main, name='site'),

    url(r'^treasure_trails', site.treasure_trails, name='treasure_trails'),
    url(r'^clue/search',  csrf_exempt(site.clue_search), name='clue_search'),
]
