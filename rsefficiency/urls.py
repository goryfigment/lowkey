from django.conf.urls import url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from rsefficiency.controllers import site, treasure_trails, grand_exchange, calculator

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', site.main, name='site'),
    url(r'^donate/$', site.donate, name='donate'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
    url(r'^sitemap\.xml$', TemplateView.as_view(template_name='sitemap.xml', content_type='text/xml')),
    url(r'^BingSiteAuth\.xml$', TemplateView.as_view(template_name='BingSiteAuth.xml', content_type='text/xml')),
    url(r'^404/$', site.error_page, name='404'),
    url(r'^500/$', site.server_error, name='500'),

    url(r'^treasure-trails/$', treasure_trails.treasure_trails, name='treasure_trails'),
    url(r'^treasure-trails/(\d+)/$', csrf_exempt(treasure_trails.clue_id_search), name='clue_id_search'),
    url(r'^clue/string_search/$',  csrf_exempt(treasure_trails.clue_string_search), name='clue_string_search'),
    url(r'^treasure-trails/([a-z]+)/$',  csrf_exempt(treasure_trails.clue_type_search), name='clue_type_search'),

    url(r'^grand-exchange/$', grand_exchange.grand_exchange, name='grand_exchange'),
    url(r'^grand-exchange/item_price/$',  csrf_exempt(grand_exchange.item_price), name='item_price'),
    url(r'^grand-exchange/item_search/$',  csrf_exempt(grand_exchange.item_string_search), name='item_string_search'),
    url(r'^grand-exchange/(\d+)/$', csrf_exempt(grand_exchange.item_id_search), name='item_id_search'),
    url(r'^item_price_graph/$', grand_exchange.item_price_graph, name='item_price_graph'),

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

    url(r'^calculator/$', calculator.calculator, name='calculator'),
    url(r'^calculator/combat-calculator$', calculator.combat_calculator, name='combat_calculator'),
    url(r'^calculator/prayer-calculator$', calculator.prayer_calculator, name='prayer_calculator'),
    url(r'^calculator/construction-calculator$', calculator.construction_calculator, name='construction_calculator'),
    url(r'^calculator/herblore-calculator$', calculator.herblore_calculator, name='herblore_calculator'),
    url(r'^calculator/magic-calculator$', calculator.magic_calculator, name='magic_calculator'),
    url(r'^calculator/cooking-calculator$', calculator.cooking_calculator, name='cooking_calculator'),
    url(r'^calculator/crafting-calculator$', calculator.crafting_calculator, name='crafting_calculator'),
    url(r'^calculator/smithing-calculator$', calculator.smithing_calculator, name='smithing_calculator'),
    url(r'^calculator/fletching-calculator$', calculator.fletching_calculator, name='fletching_calculator'),
    url(r'^calculator/highscore$', calculator.highscore, name='highscore'),
    url(r'^calculator/prices', calculator.calc_prices, name='calc_prices'),
]
