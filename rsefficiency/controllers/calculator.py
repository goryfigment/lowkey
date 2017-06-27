from django.shortcuts import render
from rsefficiency.modules.base import get_base_url, render_json
from django.http import HttpResponse
import json
import requests


def calculator(request):
    data = {
        'template': '#main_template',
        'base_url': get_base_url()
    }

    return render(request, 'calculator.html', data)


def combat_calculator(request):
    data = {
        'template': '#combat_calculator_template',
        'base_url': get_base_url()
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
