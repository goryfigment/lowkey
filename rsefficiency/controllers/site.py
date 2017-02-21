from django.shortcuts import render

from django.http import HttpResponse
from rsefficiency.models import *
from django.core import serializers
import json
from rsefficiency.modules.base import *
from django.db.models import Q


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

    clue_list = TreasureTrails.objects.filter(Q(clue__istartswith=search_value) | Q(keywords__istartswith=search_value))

    return render_json({'success': True, 'clue_list': models_to_dict(clue_list)})

# def ge_search(request):
#     if 'rs_item_name' not in request.GET:
#         data = {'success': False, 'error_id': 1}
#         return HttpResponse(json.dumps(data), 'application/json')
#
#     rs_item_name = request.GET['rs_item_name']
#
#     rs_item_json = ge_search_response(rs_item_name)


#    return HttpResponse(json.dumps(rs_item_json), 'application/json')