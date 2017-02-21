from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
import json


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