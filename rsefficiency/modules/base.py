from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
import json
import requests
import datetime
import os


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


def rs_item_json():
    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, '../controllers/static_data/rs_items.json')
        return json.load(open(file_path))
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')


def item_log_json():
    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, '../controllers/static_data/item_log.json')
        return json.load(open(file_path))
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')


def month_delta(date, delta, zero_out):
    m, y = (date.month+delta) % 12, date.year + (date.month + delta-1) // 12
    if not m:
        m = 12
    d = min(date.day, [31, 29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m-1])
    if zero_out:
        return date.replace(microsecond=0, second=0, minute=0, hour=0, day=d, month=m, year=y)
    else:
        return date.replace(day=d, month=m, year=y)


def update_item_log(item_log, item_id, buying, selling, buy_price_ts, sell_price_ts):
    now_utc = str(int(((datetime.datetime.utcnow().replace(microsecond=0, second=0)) - datetime.datetime(1970, 1, 1)).total_seconds()) * 1000)
    item = item_log[item_id]

    if buy_price_ts == 0:
        buy_price_ts = now_utc
    if sell_price_ts == 0:
        sell_price_ts = now_utc

    if buying != 0 and int(buy_price_ts) > int(item['buy_price_ts']):
        item['buying'] = buying
        item['buy_price_ts'] = buy_price_ts

    if selling != 0 and int(sell_price_ts) > int(item['sell_price_ts']):
        item['selling'] = selling
        item['sell_price_ts'] = sell_price_ts

    item['success'] = True

    item_log[item_id] = item


def access_item_log(item_id):
    item = item_log_json()[item_id]
    if item['success']:
        return {'selling': item['selling'], 'sell_price_ts': item['sell_price_ts'], 'buying': item['buying'], 'buy_price_ts': item['sell_price_ts']}
    else:
        return {'selling': 0, 'sell_price_ts': 0, 'buying': 0, 'buy_price_ts': 0}


def ge_price_updater(item_log, item_id, key, start_date):
    updated_price = 0
    updated_time = ''

    if not start_date:
        start_date = str(int((month_delta(datetime.datetime.utcnow(), -1, True) - datetime.datetime(1970, 1, 1)).total_seconds()) * 1000)

    try:
        rsbuddy_json = requests.get('http://api.rsbuddy.com/grandExchange?a=graph&g=30&i=' + str(item_id) + '&start=' + start_date).json()

        for item in reversed(rsbuddy_json):
            if key not in item or item[key] == 0:
                continue
            else:
                updated_price = item[key]
                updated_time = str(item['ts'])
                break

        if key == 'sellingPrice':
            update_item_log(item_log, item_id, 0, updated_price, 0, updated_time)
        else:
            update_item_log(item_log, item_id, updated_price, 0, updated_time, 0)
    except:
        pass

    if updated_price == 0:
        if key == 'sellingPrice':
            item_log_data = access_item_log(item_id)
            updated_price = item_log_data['selling']
            updated_time = item_log_data['sell_price_ts']
        else:
            item_log_data = access_item_log(item_id)
            updated_price = item_log_data['buying']
            updated_time = item_log_data['buy_price_ts']

    return [updated_price, updated_time]


def write_item_log(item_log):
    with open(os.path.join(os.path.dirname(__file__), '../controllers/static_data/item_log.json'), 'w') as f:
        f.write(json.dumps(item_log))
