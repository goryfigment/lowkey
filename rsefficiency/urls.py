from django.conf.urls import url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from rsefficiency.controllers import site, treasure_trails, grand_exchange

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', site.main, name='site'),

    url(r'^treasure_trails/$', treasure_trails.treasure_trails, name='treasure_trails'),
    url(r'^treasure_trails/(\d+)/$', csrf_exempt(treasure_trails.clue_id_search), name='clue_id_search'),
    url(r'^clue/string_search/$',  csrf_exempt(treasure_trails.clue_string_search), name='clue_string_search'),
    url(r'^treasure_trails/([a-z]+)/$',  csrf_exempt(treasure_trails.clue_type_search), name='clue_type_search'),

    # url(r'^grand_exchange/$', grand_exchange.grand_exchange, name='grand_exchange'),
    # url(r'^grand_exchange/item_search/$',  csrf_exempt(grand_exchange.item_string_search), name='item_string_search'),
    # url(r'^grand_exchange/(\d+)/$', csrf_exempt(grand_exchange.item_id_search), name='item_id_search'),
    # url(r'^item_price_graph/$', grand_exchange.item_price_graph, name='item_price_graph'),
    # url(r'^item_price_data/$', grand_exchange.item_price_data, name='item_price_data'),
    #
    # # url(r'^grand_exchange/high_alchemy/$',  csrf_exempt(grand_exchange.high_alchemy), name='high_alchemy'),
    # url(r'^grand_exchange/decant_potions/$',  csrf_exempt(grand_exchange.decant_potions), name='decant_potions'),
    # url(r'^grand_exchange/clean_herbs/$',  csrf_exempt(grand_exchange.clean_herbs), name='clean_herbs'),
    # url(r'^grand_exchange/potion_making/$',  csrf_exempt(grand_exchange.potion_making), name='potion_making'),
    # url(r'^grand_exchange/unfinished_potions/$',  csrf_exempt(grand_exchange.unfinished_potions), name='unfinished_potions'),
    #
    # url(r'^grand_exchange/barrows_repair/$',  csrf_exempt(grand_exchange.barrows_repair), name='barrows_repair'),
]
