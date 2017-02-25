from django.shortcuts import render
import json
import os
from django.http import HttpResponse
from rsefficiency.modules.base import get_base_url, render_json


def main(request):
    data = {
        'base_url': get_base_url()
    }

    return render(request, 'main.html', data)


def treasure_trails(request):
    data = {
        'base_url': get_base_url()
    }

    return render(request, 'treasure_trails.html', data)


def clue_search(request):
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
        riddle = clue['clue']

        if search_value.startswith('0') and clue['type'] == 'coordinate':
            search_value = search_value[1:]

        if riddle.startswith(search_value):
            data_list.append(clue)

    return render_json({'success': True, 'clue_list': data_list})
