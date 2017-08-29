from django.shortcuts import render
import json
import os
import re
from django.http import HttpResponse
from rsefficiency.modules.base import get_base_url, render_json


def treasure_trails(request):
    data = {
        'base_url': get_base_url(),
        'clue': {}
    }

    return render(request, 'treasure_trails.html', data)


def clue_string_search(request):
    if 'search_value' not in request.GET:
        data = {'success': False, 'error_id': 1, 'error_msg:': 'Data not set'}
        return HttpResponse(json.dumps(data), 'application/json')

    search_value = request.GET['search_value']
    data_list = []

    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, 'static_data/treasure_trails.json')
        clue_data = json.loads(open(file_path).read())
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')

    for clue in clue_data:
        riddle = clue['clue'].lower()
        keyword = str(clue['keywords']).lower()

        riddle_search_string = re.sub(r'[^\w]', '', riddle)
        value_search_string = re.sub(r'[^\w]', '', search_value)

        coordinate_bool = clue['type'] == "coordinate" and keyword.startswith(value_search_string)

        if riddle_search_string.startswith(value_search_string) or coordinate_bool:
            data_list.append(clue)

    return render_json({'success': True, 'clue_list': data_list})


def clue_type_search(request, clue_type):
    clue_dict = {}
    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, 'static_data/treasure_trails.json')
        clue_data = json.loads(open(file_path).read())
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')

    if clue_type == 'coordinate':
        for clue in clue_data:
            if clue['type'] == clue_type:
                if clue['clue'][1].isdigit():
                    clue_dict.setdefault(clue['clue'][:2], []).append(clue)
                else:
                    clue_dict.setdefault(clue['clue'][0], []).append(clue)
    elif clue_type == 'emote':
        for clue in clue_data:
            if clue['type'] == clue_type:
                clue['challenge'] = clue['challenge'].split(',')
                key = clue['challenge'][0]

                if clue['requirements'] != 'Nothing':
                    clue['requirements'] = clue['requirements'].split(',')

                clue_dict.setdefault(key, []).append(clue)
    elif clue_type == 'map':
        for clue in clue_data:
            if clue['type'] == clue_type:
                key = clue['difficulty']

                if key == 'Easy':
                    key = '1'
                elif key == 'Medium':
                    key = '2'
                elif key == 'Hard':
                    key = '3'
                elif key == 'Elite':
                    key = '4'
                elif key == 'Master':
                    key = '5'

                clue_dict.setdefault(key, []).append(clue)
    else:
        for clue in clue_data:
            if clue['type'] == clue_type:
                key = clue['clue'][0].upper()

                if key.isdigit():
                    key = '#'
                elif not key.isdigit() and not key.isalpha():
                    key = clue['clue'][1].upper()

                clue_dict.setdefault(key, []).append(clue)

    if clue_type == 'coordinate' or clue_type == 'map':
        clue_dict = {int(k): v for k, v in clue_dict.items()}
    elif clue_type == 'emote':
        clue_dict = {ord(k[0])*100 + ord(k[1]): v for k, v in clue_dict.items()}
    else:
        clue_dict = {ord(k): v for k, v in clue_dict.items()}

    print clue_dict

    data = {'success': True, 'base_url': get_base_url(), 'type': clue_type.title(), 'clue': json.dumps(clue_dict)}
    return render(request, 'treasure_trails.html', data)


def clue_id_search(request, clue_id):
    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, 'static_data/treasure_trails.json')
        clue_data = json.loads(open(file_path).read())
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')

    clue = clue_data[int(clue_id) - 1]

    if clue['type'] == 'emote':
        clue['challenge'] = clue['challenge'].split(',')
        if clue['requirements'] != 'Nothing':
            clue['requirements'] = clue['requirements'].split(',')

    data = {'success': True, 'base_url': get_base_url(), 'clue': json.dumps(clue), 'keyword': clue['clue'],
            'title': clue['clue']}

    return render(request, 'treasure_trails.html', data)
