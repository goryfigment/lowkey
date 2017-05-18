from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
import json
import requests


def get_base_url():
    return settings.BASE_URL


def model_to_dict(model):
    try:
        serial_obj = serializers.serialize('json', [model])
        obj_as_dict = json.loads(serial_obj)[0]['fields']
        obj_as_dict['id'] = model.pk
        return obj_as_dict
    except:
        return None


def models_to_dict(model_list):

    model_list = list(model_list)
    my_list = []
    for model in model_list:
        model_dict = model_to_dict(model)
        if model_dict:
            my_list.append(model_dict)

    return my_list


def render_json(data):
    return HttpResponse(json.dumps(data), 'application/json')


def ge_price_updater(item_id, key):
    rsbuddy_json = requests.get('http://api.rsbuddy.com/grandExchange?a=graph&g=30&i=' + str(item_id)).json()
    updated_price = 0
    updated_time = ''

    for item in reversed(rsbuddy_json):
        if key not in item or item[key] == 0:
            continue
        else:
            updated_price = item[key]
            updated_time = str(item['ts'])
            break

    if updated_price == 0:
        print item_id
        print rsbuddy_json

    return [updated_price, updated_time]
