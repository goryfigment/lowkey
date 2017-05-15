from django.shortcuts import render
import json
import math
import requests
import os
import re
import grequests
from django.http import HttpResponse
from rsefficiency.modules.base import get_base_url, render_json, ge_price_updater


def grand_exchange(request):
    frontpage_data = frontpage()

    data = {
        'base_url': get_base_url(),
        'high_alch': frontpage_data['high_alch_list'],
        'result_list': {},
        'item_data': {}
    }

    return render(request, 'grand_exchange.html', data)


def item_string_search(request):
    if 'search_value' not in request.GET:
        data = {'success': False, 'error_id': 1, 'error_msg:': 'Data not set'}
        return HttpResponse(json.dumps(data), 'application/json')

    search_value = request.GET['search_value']
    data_list = []

    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, 'static_data/rs_items.json')
        item_data = json.load(open(file_path))
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')

    for key, item in item_data.iteritems():
        item_name = item['name'].lower()

        item_search_string = re.sub(r'[^\w]', '', item_name)
        value_search_string = re.sub(r'[^\w]', '', search_value)

        if item_search_string.startswith(value_search_string):
            data_list.append(item)

    data_list = sorted(data_list, key=lambda k: k['name'])

    return render_json({'success': True, 'item_list': data_list})


def item_price_graph(request):
    if 'item_id' not in request.GET and 'start_time' not in request.GET:
        data = {'success': False, 'error_id': 1, 'error_msg:': 'Data not set', 'data': request.GET}
        return HttpResponse(json.dumps(data), 'application/json')

    item_id = request.GET['item_id']
    start_time = request.GET['start_time']

    osbuddy_base_url = 'http://api.rsbuddy.com/grandExchange'

    urls = [
        'http://services.runescape.com/m=itemdb_oldschool/api/graph/' + item_id + '.json',
        osbuddy_base_url + '?a=graph&g=1440&i=' + item_id + '&start=' + start_time,
        osbuddy_base_url + '?a=graph&g=30&i=' + item_id
    ]

    responses = grequests.map(grequests.get(u) for u in urls)
    osrs_price_graph = responses[0].json()['daily']
    osrs_price_array = sorted(osrs_price_graph)

    current_price = osrs_price_graph[osrs_price_array[-1]]
    previous_price = osrs_price_graph[osrs_price_array[-2]]

    margin = current_price - previous_price
    margin_ratio = round(100.0 * margin/current_price, 1)

    return render_json({'success': True, 'osrs_price_graph': osrs_price_graph, 'osbuddy_price_graph': responses[1].json(),
                        'osbuddy_price_history': responses[2].json(), 'current_price': current_price,
                        'previous_price': previous_price, 'margin': margin, 'margin_ratio': margin_ratio})


def item_price_data(request):
    if 'item_id' not in request.GET:
        data = {'success': False, 'error_id': 1, 'error_msg:': 'Data not set', 'data': request.GET}
        return HttpResponse(json.dumps(data), 'application/json')

    item_id = str(request.GET['item_id'])

    urls = [
        'http://services.runescape.com/m=itemdb_oldschool/api/graph/' + item_id + '.json',
        'http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + item_id
    ]

    responses = grequests.map(grequests.get(u) for u in urls)

    osrs_price_graph = responses[0].json()['daily']
    osrs_price_array = sorted(osrs_price_graph)

    return render_json({'osrs_price_graph': responses[0].json()['daily'], 'osbuddy_price_data': responses[1].json(),
                        'current_price': osrs_price_graph[osrs_price_array[-1]], 'previous_price': osrs_price_graph[osrs_price_array[-2]]})


def frontpage():
    rsbuddy_json = requests.get('https://rsbuddy.com/exchange/summary.json', verify=False).json()

    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, 'static_data/rs_items.json')
        item_json = json.load(open(file_path))
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')

    nature_rune_buy_avg = rsbuddy_json['561']['buy_average']

    high_alch_list = []
    margins_list = []

    for key, item in item_json.iteritems():
        rsbuddy_json_item = rsbuddy_json[key]
        item_buy_avg = rsbuddy_json_item['buy_average']
        item_sell_avg = rsbuddy_json_item['sell_average']

        if item_buy_avg == 0:
            continue

        total_cost = item['high_alch'] - (item_buy_avg + nature_rune_buy_avg)

        if total_cost < -250:
            continue

        high_alch_list.append({'item_data': item, 'total_cost': total_cost, 'buy_price': item_buy_avg})

        if item_buy_avg == 0 and item_sell_avg == 0:
            continue

        margin = item_buy_avg - item_sell_avg

        margins_list.append({'item_data': item, 'total_cost': margin, 'buy_price': item_buy_avg, 'sell_price': item_sell_avg})

    high_alch_list = sorted(high_alch_list, key=lambda k: k['total_cost'], reverse=True)
    margins_list = sorted(margins_list, key=lambda k: k['total_cost'], reverse=True)

    data = {
        'high_alch_list': high_alch_list[:10],
        'margins_list': margins_list[:10]
    }

    return data


def decant_potions(request):
    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, 'static_data/rs_items.json')
        item_json = json.load(open(file_path))
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')

    potion_list = ['3038', '3036', '3034', '3032', '12911', '12909', '12907', '12905', '12919', '12917', '12915',
                   '12913', '5949', '5947', '5945', '5943', '5958', '5956', '5954', '5952', '2458', '2456', '2454',
                   '2452', '179', '177', '175', '2446', '125', '123', '121', '2428', '9745', '9743', '9741', '9739',
                   '6476', '6474', '6472', '6470', '137', '135', '133', '2432', '3014', '3012', '3010', '3008', '11957',
                   '11955', '11953', '11951', '155', '153', '151', '2438', '7666', '7664', '7662', '7660', '4423',
                   '4421', '4419', '4417', '10004', '10002', '10000', '9998', '3046', '3044', '3042', '3040', '3428',
                   '3426', '3424', '3422', '143', '141', '139', '2434', '173', '171', '169', '2444', '4848', '4846',
                   '4844', '4842', '131', '129', '127', '2430', '3436', '3434', '3432', '3430', '10931', '10929',
                   '10927', '10925', '6691', '6689', '6687', '6685', '3414', '3412', '3410', '3408', '12631', '12629',
                   '12627', '12625', '119', '117', '115', '113', '149', '147', '145', '2436', '12701', '12699', '12697',
                   '12695', '167', '165', '163', '2442', '3022', '3020', '3018', '3016', '3030', '3028', '3026', '3024',
                   '161', '159', '157', '2440', '185', '183', '181', '2448', '193', '191', '189', '2450']

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in potion_list]

    data_list = []

    responses = grequests.map(grequests.get(u) for u in urls)

    for i in xrange(0, 148, 4):
        two_dose = i + 1
        three_dose = i + 2
        four_dose = i + 3

        one_dose_price = responses[i].json()['selling']
        two_dose_price = responses[two_dose].json()['selling']
        three_dose_price = responses[three_dose].json()['selling']
        four_dose_price = responses[four_dose].json()['buying']

        one_dose_item_json = item_json[potion_list[i]]
        two_dose_item_json = item_json[potion_list[two_dose]]
        three_dose_item_json = item_json[potion_list[three_dose]]
        four_dose_item_json = item_json[potion_list[four_dose]]

        one_dose_id = one_dose_item_json['id']
        two_dose_id = two_dose_item_json['id']
        three_dose_id = three_dose_item_json['id']
        four_dose_id = four_dose_item_json['id']

        one_dose_updated_time = ''
        two_dose_updated_time = ''
        three_dose_updated_time = ''
        four_dose_updated_time = ''

        if one_dose_price == 0:
            updated_data = ge_price_updater(one_dose_id, 'sellingPrice')
            one_dose_price = updated_data[0]
            one_dose_updated_time = updated_data[1]

        if two_dose_price == 0:
            updated_data = ge_price_updater(two_dose_id, 'sellingPrice')
            two_dose_price = updated_data[0]
            two_dose_updated_time = updated_data[1]

        if three_dose_price == 0:
            updated_data = ge_price_updater(three_dose_id, 'sellingPrice')
            three_dose_price = updated_data[0]
            three_dose_updated_time = updated_data[1]

        if four_dose_price == 0:
            updated_data = ge_price_updater(four_dose_id, 'buyingPrice')
            four_dose_price = updated_data[0]
            four_dose_updated_time = updated_data[1]

        two_price_per_dose = int(math.ceil(float(two_dose_price) / 2)) if two_dose_price <= 1 else int(round(float(two_dose_price) / 2))
        three_price_per_dose = int(math.ceil(float(three_dose_price) / 3)) if three_dose_price <= 1 else int(round(float(three_dose_price) / 3))

        minimum_price = one_dose_price
        cheapest_dose = 'one'

        if two_price_per_dose < minimum_price and two_price_per_dose < three_price_per_dose:
            minimum_price = two_price_per_dose
            cheapest_dose = 'two'
        elif three_price_per_dose < minimum_price:
            minimum_price = three_price_per_dose
            cheapest_dose = 'three'

        cheapest_cost = 4*minimum_price
        profit = four_dose_price - cheapest_cost

        item_data = {'name': one_dose_item_json['name'].replace('(1)', ''), 'cheapest_cost': cheapest_cost,
            'limit': four_dose_item_json['limit'], 'file_name': four_dose_item_json['file_name'],
            'potion_id': four_dose_item_json['id'], 'one_dose_cost': one_dose_price, 'two_dose_cost': two_dose_price,
            'three_dose_cost': three_dose_price, 'four_dose_cost': four_dose_price, 'profit': profit,
            'cheapest_dose': cheapest_dose}

        if one_dose_updated_time != '':
            item_data['one_dose_updated_time'] = one_dose_updated_time

        if two_dose_updated_time != '':
            item_data['two_dose_updated_time'] = two_dose_updated_time

        if three_dose_updated_time != '':
            item_data['three_dose_updated_time'] = three_dose_updated_time

        if four_dose_updated_time != '':
            item_data['four_dose_updated_time'] = four_dose_updated_time

        data_list.append(item_data)

    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)
    data = {'base_url': get_base_url(), 'item_data': {}, 'high_alch': {}, 'result_list': {'list': data_list}, 'result_type': 'decant_potions'}
    return render(request, 'grand_exchange.html', data)


def clean_herbs(request):
    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, 'static_data/rs_items.json')
        item_json = json.load(open(file_path))
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')

    herblore_list = ['199', '249', '201', '251', '203', '253', '205', '255', '207', '257', '3049', '2998', '209', '259',
                     '211', '261', '213', '263', '3051', '3000', '215', '265', '2485', '2481', '217', '267', '219',
                     '269']

    requirements = [3, 5, 11, 20, 25, 30, 40, 48, 54, 59, 65, 67, 70, 75]

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in herblore_list]

    data_list = []

    responses = grequests.map(grequests.get(u) for u in urls)

    for i in xrange(0, 28, 2):
        clean = i + 1

        grimy_item_json = item_json[herblore_list[i]]
        clean_item_json = item_json[herblore_list[clean]]

        grimy_cost = responses[i].json()['selling']
        clean_sale = responses[clean].json()['buying']
        grimy_id = grimy_item_json['id']
        clean_id = clean_item_json['id']
        grimy_updated_time = ''
        clean_updated_time = ''

        if grimy_cost == 0:
            updated_data = ge_price_updater(grimy_id, 'sellingPrice')
            grimy_cost = updated_data[0]
            grimy_updated_time = updated_data[1]

        if clean_sale == 0:
            updated_data = ge_price_updater(clean_id, 'buyingPrice')
            clean_sale = updated_data[0]
            clean_updated_time = updated_data[1]

        profit = clean_sale - grimy_cost

        item_data = {'clean_file_name': clean_item_json['file_name'], 'grimy_buy_limit': grimy_item_json['limit'],
            'grimy_file_name': grimy_item_json['file_name'], 'name': clean_item_json['name'],
            'grimy_id': grimy_id, 'clean_id': clean_id, 'grimy_cost': grimy_cost, 'clean_sale': clean_sale,
            'profit': profit, 'requirement': requirements[i / 2]}

        if grimy_updated_time != '':
            item_data['grimy_updated_time'] = grimy_updated_time

        if clean_updated_time != '':
            item_data['clean_updated_time'] = clean_updated_time

        data_list.append(item_data)

    data = {'base_url': get_base_url(), 'item_data': {}, 'high_alch': {}, 'result_list': {'list': data_list}, 'result_type': 'clean_herbs'}
    return render(request, 'grand_exchange.html', data)


def barrows_repair(request):
    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, 'static_data/rs_items.json')
        item_json = json.load(open(file_path))
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')

    barrows_list = ['4718', '4890', '4716', '4884', '4720', '4896', '4722', '4902',
                    '4710', '4866', '4708', '4860', '4712', '4872', '4714', '4878',
                    '4726', '4914', '4724', '4908', '4728', '4920', '4730', '4926',
                    '4734', '4938', '4732', '4932', '4736', '4944', '4738', '4950',
                    '4755', '4986', '4753', '4980', '4757', '4992', '4759', '4998']

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in barrows_list]

    weapon_repair = 100000
    helmet_repair = 60000
    body_repair = 90000
    leg_repair = 80000

    if 'smithing_level' in request.GET:
        smithing_level = int(request.GET['smithing_level'])
        weapon_repair = (1 - (smithing_level / 200)) * weapon_repair
        helmet_repair = (1 - (smithing_level / 200)) * helmet_repair
        body_repair = (1 - (smithing_level / 200)) * body_repair
        leg_repair = (1 - (smithing_level / 200)) * leg_repair

    responses = grequests.map(grequests.get(u) for u in urls)

    data_list = []

    for i in xrange(0, 40, 2):
        broken = i + 1

        fixed_item_json = item_json[barrows_list[i]]
        broken_item_json = item_json[barrows_list[broken]]
        fixed_item_id = fixed_item_json['id']
        broken_item_id = broken_item_json['id']
        broken_updated_time = ''
        fixed_updated_time = ''

        broken_cost = responses[broken].json()['selling']
        fixed_sale = responses[i].json()['buying']

        if broken % 8 == 1:
            repair_cost = weapon_repair
        elif broken % 8 == 3:
            repair_cost = helmet_repair
        elif broken % 8 == 5:
            repair_cost = body_repair
        elif broken % 8 == 7:
            repair_cost = leg_repair

        if broken_cost == 0:
            updated_data = ge_price_updater(broken_item_id, 'sellingPrice')
            broken_cost = updated_data[0]
            broken_updated_time = updated_data[1]

        if fixed_sale == 0:
            updated_data = ge_price_updater(fixed_item_id, 'buyingPrice')
            broken_cost = updated_data[0]
            broken_updated_time = updated_data[1]

        profit = fixed_sale - (broken_cost + repair_cost)

        item_data = {'fixed_file_name': fixed_item_json['file_name'], 'broken_buy_limit': fixed_item_json['limit'],
            'broken_file_name': broken_item_json['file_name'], 'name': fixed_item_json['name'],
            'fixed_id': fixed_item_id, 'broken_id': broken_item_id,
            'broken_cost': broken_cost, 'fixed_sale': fixed_sale, 'profit': profit, 'repair': repair_cost}

        if broken_updated_time != '':
            item_data['broken_updated_time'] = broken_updated_time

        if fixed_updated_time != '':
            item_data['fixed_updated_time'] = fixed_updated_time

        data_list.append(item_data)

    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)

    data = {'base_url': get_base_url(), 'item_data': {}, 'high_alch': {}, 'result_list': {'list': data_list}, 'result_type': 'barrows_repair'}
    return render(request, 'grand_exchange.html', data)


def potion_making(request):
    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, 'static_data/rs_items.json')
        item_json = json.load(open(file_path))
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')

    item_list = ['227', '2998', '2152', '3034', '5954', '12934', '12907', '269', '12915', '5935', '6049', '5945', '259', '6051', '2481', '241', '2454', '251', '235', '175', '249', '221', '121', '255', '9736', '9741', '257', '239', '133', '1975', '3010', '11994', '11953', '261', '231', '151', '223', '1550', '7650', '7662', '4419', '10111', '10000', '3138', '3042', '139', '267', '245', '169', '127', '6693', '6687', '253', '592', '3410', '3018', '12640', '12627', '225', '115', '145', '157', '163', '12697', '265', '2970', '3000', '3026', '263', '181', '247', '189']

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in item_list]

    responses = grequests.map(grequests.get(u) for u in urls)
    data_list = []
    response_dict = {}

    for i, item in enumerate(item_list):
        response_dict[item] = responses[i].json()

    potion_dict = [
        {'potion': '3034', 'ingredients': ['2998', '2152']},
        {'potion': '12907', 'ingredients': ['5954', '12934'], 'multiples': [1, 15]},
        {'potion': '12915', 'ingredients': ['269', '12907']},
        {'potion': '5945', 'ingredients': ['2998', '5935', '6049']},
        {'potion': '5954', 'ingredients': ['259', '5935', '6051']},
        {'potion': '2454', 'ingredients': ['2481', '241']},
        {'potion': '175', 'ingredients': ['251', '235']},
        {'potion': '121', 'ingredients': ['249', '221']},
        {'potion': '9741', 'ingredients': ['255', '9736']},
        {'potion': '133', 'ingredients': ['257', '239']},
        {'potion': '3010', 'ingredients': ['255', '1975']},
        {'potion': '11953', 'ingredients': ['2454', '11994'], 'multiples': [1, 3]},
        {'potion': '151', 'ingredients': ['261', '231']},
        {'potion': '7662', 'ingredients': ['255', '223', '1550', '7650']},
        {'potion': '4419', 'ingredients': ['249', '255', '251'], 'multiples': [2, 1, 1]},
        {'potion': '10000', 'ingredients': ['261', '10111']},
        {'potion': '3042', 'ingredients': ['2481', '3138']},
        {'potion': '139', 'ingredients': ['257', '231']},
        {'potion': '169', 'ingredients': ['267', '245']},
        {'potion': '127', 'ingredients': ['255', '223']},
        {'potion': '6687', 'ingredients': ['2998', '6693']},
        {'potion': '3410', 'ingredients': ['253', '592']},
        {'potion': '12627', 'ingredients': ['3018', '12640'], 'multiples': [1, 3]},
        {'potion': '115', 'ingredients': ['253', '225']},
        {'potion': '145', 'ingredients': ['259', '221']},
        {'potion': '12697', 'ingredients': ['269', '145', '157', '163']},
        {'potion': '163', 'ingredients': ['265', '239']},
        {'potion': '3018', 'ingredients': ['261', '2970']},
        {'potion': '3026', 'ingredients': ['3000', '223']},
        {'potion': '157', 'ingredients': ['263', '225']},
        {'potion': '181', 'ingredients': ['259', '235']},
        {'potion': '189', 'ingredients': ['269', '247']}
    ]

    vial_of_water_cost = response_dict['227']['selling']
    vial_of_water_updated_time = ''

    if vial_of_water_cost == 0:
        updated_data = ge_price_updater(227, 'sellingPrice')
        vial_of_water_cost = updated_data[0]
        vial_of_water_updated_time = updated_data[1]

    for pot in potion_dict:
        potion = pot['potion']
        potion_item_json = item_json[potion]
        potion_sale = response_dict[potion]['buying']
        ingredients = pot['ingredients']
        ingredient_list = []

        total_cost = vial_of_water_cost

        for i, ingredient in enumerate(ingredients):
            ingredient_json = item_json[ingredient]
            buy_price = response_dict[ingredient]['selling']
            ingredient_updated_time = ''

            if buy_price == 0:
                updated_data = ge_price_updater(ingredient, 'sellingPrice')
                buy_price = updated_data[0]
                ingredient_updated_time = updated_data[1]

            ingredient_dict = {'id': ingredient, 'name': ingredient_json['name'], 'limit': ingredient_json['limit'],
                               'file_name': ingredient_json['file_name'], 'buy_price': buy_price}

            if 'multiples' in pot:
                multiple = pot['multiples'][i]
                total_cost = total_cost + (buy_price*multiple)
                if multiple > 1:
                    ingredient_dict['multiple'] = {}
                    ingredient_dict['multiple'][ingredient] = multiple
            else:
                total_cost = total_cost + buy_price

            if ingredient_updated_time != '':
                ingredient_dict['ingredient_updated_time'] = ingredient_updated_time

            ingredient_list.append(ingredient_dict)

        if potion_sale == 0:
            updated_data = ge_price_updater(potion, 'buyingPrice')
            potion_sale = updated_data[0]
            potion_updated_time = updated_data[1]

        profit = potion_sale - total_cost

        item_data = {'file_name': potion_item_json['file_name'], 'limit': potion_item_json['limit'],
                     'name': potion_item_json['name'].replace('(3)', ''), 'id': potion, 'total_cost': total_cost,
                     'ingredient_list': ingredient_list, 'vial_of_water_cost': vial_of_water_cost,
                     'potion_sale': potion_sale, 'profit': profit}

        if potion_updated_time != '':
            item_data['potion_updated_time'] = potion_updated_time

        data_list.append(item_data)

    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)

    data = {'base_url': get_base_url(), 'item_data': {}, 'high_alch': {}, 'result_list': {'list': data_list}, 'result_type': 'potion_making'}
    return render(request, 'grand_exchange.html', data)


def unfinished_potions(request):
    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, 'static_data/rs_items.json')
        item_json = json.load(open(file_path))
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')

    potion_list = ['227', '249', '91', '251', '93', '253', '95', '255', '97', '257', '99', '2998', '3002', '259', '101',
                   '261', '103', '263', '105', '3000', '3004', '265', '107', '2481', '2483', '267', '109', '269', '111']

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in potion_list]

    data_list = []

    responses = grequests.map(grequests.get(u) for u in urls)

    vial_of_water_cost = responses[0].json()['selling']
    vial_of_water_updated_time = ''

    if vial_of_water_cost == 0:
        updated_data = ge_price_updater(227, 'sellingPrice')
        vial_of_water_cost = updated_data[0]
        vial_of_water_updated_time = updated_data[1]

    for i in xrange(1, 29, 2):
        potion = i + 1

        herb_item_json = item_json[potion_list[i]]
        potion_item_json = item_json[potion_list[potion]]

        herb_cost = responses[i].json()['selling']
        potion_sale = responses[potion].json()['buying']
        herb_id = herb_item_json['id']
        potion_id = potion_item_json['id']
        herb_updated_time = ''
        potion_updated_time = ''

        if herb_cost == 0:
            updated_data = ge_price_updater(herb_id, 'sellingPrice')
            herb_cost = updated_data[0]
            herb_updated_time = updated_data[1]

        if potion_sale == 0:
            updated_data = ge_price_updater(potion_id, 'buyingPrice')
            potion_sale = updated_data[0]
            potion_updated_time = updated_data[1]

        profit = potion_sale - (vial_of_water_cost + herb_cost)

        item_data = {'herb_file_name': herb_item_json['file_name'], 'limit': herb_item_json['limit'],
            'potion_file_name': potion_item_json['file_name'], 'name': potion_item_json['name'],
            'herb_id': herb_id, 'potion_id': potion_id, 'herb_cost': herb_cost, 'potion_sale': potion_sale,
            'profit': profit, 'vial_of_water_cost': vial_of_water_cost}

        if herb_updated_time != '':
            item_data['herb_updated_time'] = herb_updated_time

        if potion_updated_time != '':
            item_data['potion_updated_time'] = potion_updated_time

        data_list.append(item_data)

    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)

    data = {'base_url': get_base_url(), 'item_data': {}, 'high_alch': {}, 'result_list': {'list': data_list}, 'result_type': 'unfinished_potions'}
    return render(request, 'grand_exchange.html', data)


def item_id_search(request, item_id):
    try:
        my_dir = os.path.dirname(__file__)
        file_path = os.path.join(my_dir, 'static_data/rs_items.json')
        item_json = json.load(open(file_path))
    except:
        data = {'success': False, 'error_id': 2, 'error_msg:': 'IO Error', 'directory': file_path}
        return HttpResponse(json.dumps(data), 'application/json')

    data = {'base_url': get_base_url(), 'item_data': item_json[item_id], 'high_alch': {}, 'result_list': {}}
    return render(request, 'grand_exchange.html', data)

