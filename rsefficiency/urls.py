from django.conf.urls import url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from rsefficiency.controllers import site, treasure_trails, grand_exchange

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', site.main, name='site'),

    url(r'^treasure-trails/$', treasure_trails.treasure_trails, name='treasure_trails'),
    url(r'^treasure-trails/(\d+)/$', csrf_exempt(treasure_trails.clue_id_search), name='clue_id_search'),
    url(r'^clue/string_search/$',  csrf_exempt(treasure_trails.clue_string_search), name='clue_string_search'),
    url(r'^treasure-trails/([a-z]+)/$',  csrf_exempt(treasure_trails.clue_type_search), name='clue_type_search'),

    url(r'^grand-exchange/$', grand_exchange.grand_exchange, name='grand_exchange'),
    url(r'^grand-exchange/item_price/$',  csrf_exempt(grand_exchange.item_price), name='item_price'),
    url(r'^grand-exchange/item_search/$',  csrf_exempt(grand_exchange.item_string_search), name='item_string_search'),
    url(r'^grand-exchange/(\d+)/$', csrf_exempt(grand_exchange.item_id_search), name='item_id_search'),
    url(r'^item_price_graph/$', grand_exchange.item_price_graph, name='item_price_graph'),
    url(r'^item_price_data/$', grand_exchange.item_price_data, name='item_price_data'),

    url(r'^grand-exchange/decant-potions/$',  csrf_exempt(grand_exchange.decant_potions), name='decant_potions'),
    url(r'^grand-exchange/clean-herbs/$',  csrf_exempt(grand_exchange.clean_herbs), name='clean_herbs'),
    url(r'^grand-exchange/potion-making/$',  csrf_exempt(grand_exchange.potion_making), name='potion_making'),
    url(r'^grand-exchange/unfinished-potions/$',  csrf_exempt(grand_exchange.unfinished_potions), name='unfinished_potions'),

    url(r'^grand-exchange/barrows-repair/$',  csrf_exempt(grand_exchange.barrows_repair), name='barrows_repair'),
    url(r'^grand-exchange/plank-making/$',  csrf_exempt(grand_exchange.plank_making), name='plank_making'),
    url(r'^grand-exchange/enchant-bolts/$',  csrf_exempt(grand_exchange.enchant_bolts), name='enchant_bolts'),
    url(r'^grand-exchange/tan-leather/$',  csrf_exempt(grand_exchange.tan_leather), name='tan_leather'),
    url(r'^grand-exchange/item-sets/$',  csrf_exempt(grand_exchange.item_sets), name='item_sets'),
    url(r'^grand-exchange/magic-tablets/$',  csrf_exempt(grand_exchange.magic_tablets), name='magic_tablets'),
]
