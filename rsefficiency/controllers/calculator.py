from django.shortcuts import render
from rsefficiency.modules.base import get_base_url, render_json, item_log_json, access_item_log, ge_price_updater, update_item_log, write_item_log
from django.http import HttpResponse
import json
import requests
import grequests
from rsefficiency.modules.calc_list import *


def calculator(request):
    data = {
        'template': '#main-template',
        'base_url': get_base_url(),
        'calc_data': {}
    }

    return render(request, 'calculator.html', data)


def combat_calculator(request):
    data = {
        'template': '#combat-calculator-template',
        'base_url': get_base_url(),
        'calc_data': {}
    }

    return render(request, 'calculator.html', data)


def prayer_calculator(request):
    data = {
        'template': '#prayer-calculator-template',
        'base_url': get_base_url(),
        'calc_data': {'bones_list': bones_list, 'ensouled_list': ensouled_list},
        'calc_type': 'Prayer'
    }

    return render(request, 'calculator.html', data)


def herblore_calculator(request):
    data = {
        'template': '#herblore-calculator-template',
        'base_url': get_base_url(),
        'calc_data': {'herblore_list': herblore_dict},
        'calc_type': 'Herblore'
    }

    return render(request, 'calculator.html', data)


def construction_calculator(request):
    data = {
        'template': '#construction-calculator-template',
        'base_url': get_base_url(),
        'calc_data': {'plank_list': plank_list},
        'calc_type': 'Construction'
    }

    return render(request, 'calculator.html', data)


def magic_calculator(request):
    data = {
        'template': '#magic-calculator-template',
        'base_url': get_base_url(),
        'calc_data': {'normal_book': normal_book, 'lunar_book': lunar_book},
        'calc_type': 'Magic'
    }

    return render(request, 'calculator.html', data)


def cooking_calculator(request):
    data = {
        'template': '#cooking-calculator-template',
        'base_url': get_base_url(),
        'calc_data': {'cooking_list': cooking_dict},
        'calc_type': 'Cooking'
    }

    return render(request, 'calculator.html', data)


def crafting_calculator(request):
    data = {
        'template': '#crafting-calculator-template',
        'base_url': get_base_url(),
        'calc_data': {'crafting_list': crafting_dict},
        'calc_type': 'Crafting'
    }

    return render(request, 'calculator.html', data)


def smithing_calculator(request):
    data = {
        'template': '#smithing-calculator-template',
        'base_url': get_base_url(),
        'calc_data': {'smithing_list': smithing_dict},
        'calc_type': 'Smithing'
    }

    return render(request, 'calculator.html', data)


def highscore(request):
    if 'username' not in request.GET and 'type' not in request.GET:
        data = {'success': False, 'error_id': 1, 'error_msg:': 'Data not set'}
        return HttpResponse(json.dumps(data), 'application/json')

    username = request.GET['username']
    highscore_type = request.GET['type']

    response = requests.get('http://services.runescape.com/m=' + highscore_type + '/index_lite.ws?player=' + username).text.split('\n')
    skills = ['Overall','Attack','Defence','Strength','Hitpoints','Ranged','Prayer','Magic','Cooking','Woodcutting','Fletching','Fishing','Firemaking','Crafting','Smithing','Mining','Herblore','Agility','Thieving','Slayer','Farming','Runecrafting','Hunter','Construction']
    skill_dict = {}
    for i, result in enumerate(response):
        skill_data = result.split(',')
        if len(skill_data) == 3:
            current_skill = skills[i]
            skill_dict[current_skill] = {}
            skill_dict[current_skill]['rank'] = skill_data[0]
            skill_dict[current_skill]['level'] = int(skill_data[1])
            skill_dict[current_skill]['exp'] = int(skill_data[2])

    return render_json(skill_dict)


def calc_prices(request):
    if 'calc_type' not in request.GET:
        data = {'success': False, 'error_id': 1, 'error_msg:': 'Data not set'}
        return HttpResponse(json.dumps(data), 'application/json')

    item_log = item_log_json()
    calc_type = request.GET['calc_type']
    item_list = []

    if calc_type == 'Prayer':
        item_list = prayer_list
    elif calc_type == 'Construction':
        item_list = construction_list
    elif calc_type == 'Magic':
        item_list = magic_list
    elif calc_type == 'Herblore':
        item_list = herblore_list
    elif calc_type == 'Cooking':
        item_list = cooking_list
    elif calc_type == 'Crafting':
        item_list = crafting_list
    elif calc_type == 'Smithing':
        item_list = smithing_list

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in item_list]
    responses = grequests.map(grequests.get(u) for u in urls)

    item_dict = {}

    for i, item in enumerate(item_list):
        sell_updated_time = 0
        buy_updated_time = 0

        try:
            response = responses[i].json()
            selling = response['selling']
            buying = response['buying']
            sell_quantity = response['sellingQuantity']
        except:
            item_log_data = access_item_log(item)
            selling = item_log_data['selling']
            sell_quantity = 0
            sell_updated_time = item_log_data['sell_price_ts']

        if selling == 0:
            updated_data = ge_price_updater(item_log, item, 'sellingPrice', False)
            selling = updated_data[0]
            sell_updated_time = updated_data[1]

        if buying == 0:
            updated_data = ge_price_updater(item_log, item, 'buyingPrice', False)
            buying = updated_data[0]
            buy_updated_time = updated_data[1]

        item_data = {'selling': selling, 'sell_quantity': sell_quantity, 'buying': buying}

        if sell_updated_time != 0:
            item_data['sell_updated_time'] = sell_updated_time
        if buy_updated_time != 0:
            item_data['buy_updated_time'] = buy_updated_time

        update_item_log(item_log, item, buying, selling, buy_updated_time, sell_updated_time)
        item_dict[item] = item_data

    write_item_log(item_log)
    return render_json(item_dict)


