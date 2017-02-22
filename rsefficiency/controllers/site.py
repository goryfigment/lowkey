from django.shortcuts import render
import json
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
        data = {'success': False, 'error_id': 1}
        return HttpResponse(json.dumps(data), 'application/json')

    search_value = request.GET['search_value']

    clue_data = json.loads(open('static_data/treasure_trails.json').read())
    data_list = []

    for clue in clue_data:
        riddle = clue['clue']

        if clue['clue_types'] == 'coordinate' and riddle.startswith('0') and not search_value.startswith('0'):
            if riddle[1:].startswith(search_value):
                data_list.append(clue)
                continue

        if riddle.startswith(search_value):
            data_list.append(clue)

    return render_json({'success': True, 'clue_list': data_list})
