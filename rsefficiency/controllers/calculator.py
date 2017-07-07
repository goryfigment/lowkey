from django.shortcuts import render
from rsefficiency.modules.base import get_base_url, render_json, item_log_json, access_item_log, ge_price_updater, update_item_log, write_item_log
from django.http import HttpResponse
import json
import requests
import grequests
from rsefficiency.modules.calc_list import *


def calculator(request):
    data = {
        'template': '#main_template',
        'base_url': get_base_url(),
        'calc_data': {}
    }

    return render(request, 'calculator.html', data)


def combat_calculator(request):
    data = {
        'template': '#combat_calculator_template',
        'base_url': get_base_url(),
        'calc_data': {}
    }

    return render(request, 'calculator.html', data)


def prayer_calculator(request):
    data = {
        'template': '#prayer_calculator_template',
        'base_url': get_base_url(),
        'calc_data': {'bones_list': bones_list, 'ensouled_list': ensouled_list},
        'calc_type': 'Prayer'
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

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in item_list]
    responses = grequests.map(grequests.get(u) for u in urls)

    item_dict = {}

    for i, item in enumerate(item_list):
        sell_updated_time = 0

        try:
            response = responses[i].json()
            selling = response['selling']
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

        item_data = {'selling': selling, 'sell_quantity': sell_quantity}

        if sell_updated_time != 0:
            item_data['sell_updated_time'] = sell_updated_time

        update_item_log(item_log, item, 0, selling, 0, sell_updated_time)
        item_dict[item] = item_data

    write_item_log(item_log)
    return render_json(item_dict)


