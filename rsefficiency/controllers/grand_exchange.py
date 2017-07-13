from django.shortcuts import render
import json
import math
import re
import grequests
from random import randint
from django.http import HttpResponse
from rsefficiency.modules.base import get_base_url, render_json, ge_price_updater, rs_item_json, item_log_json, update_item_log, write_item_log, access_item_log
from rsefficiency.modules.ge_list import *


def grand_exchange(request):
    item_json = rs_item_json()
    item_log = item_log_json()
    random_int = randint(6, 7)
    random_list = []
    list_title = ''

    # if random_int == 1:
    #     random_list = easy_clue_list
    #     list_title = 'Easy Clue Rewards'
    # elif random_int == 2:
    #     random_list = medium_clue_list
    #     list_title = 'Medium Clue Rewards'
    # if random_int == 3:
    #     random_list = hard_clue_list
    #     list_title = 'Hard Clue Rewards'
    # elif random_int == 4:
    #     random_list = elite_clue_list
    #     list_title = 'Elite Clue Rewards'
    # elif random_int == 5:
    #     random_list = master_clue_list
    #     list_title = 'Master Clue Rewards'
    if random_int == 6:
        random_list = raid_reward_list
        list_title = 'Raid Unique Rewards'
    elif random_int == 7:
        random_list = gwd_drops
        list_title = 'GWD Unique Drops'

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in random_list]
    data_list = []
    responses = grequests.map(grequests.get(u) for u in urls)

    for i, item in enumerate(random_list):
        random_item_json = item_json[item]
        buy_updated_time = 0
        sell_updated_time = 0

        try:
            response = responses[i].json()
            buying = response['buying']
            selling = response['selling']
            buy_quantity = response['buyingQuantity']
            sell_quantity = response['sellingQuantity']
        except:
            item_log_data = access_item_log(item)
            buying = item_log_data['buying']
            selling = item_log_data['selling']
            buy_quantity = 0
            sell_quantity = 0
            buy_updated_time = item_log_data['buy_price_ts']
            sell_updated_time = item_log_data['sell_price_ts']

        if buying == 0:
            updated_data = ge_price_updater(item_log, item, 'buyingPrice', False)
            buying = updated_data[0]
            buy_updated_time = updated_data[1]

        if selling == 0:
            updated_data = ge_price_updater(item_log, item, 'sellingPrice', False)
            selling = updated_data[0]
            sell_updated_time = updated_data[1]

        profit = buying - selling

        item_data = {'name': random_item_json['name'], 'buying': buying, 'selling': selling, 'id': item,
            'limit': random_item_json['limit'], 'file_name': random_item_json['file_name'], 'buy_quantity': buy_quantity,
            'sell_quantity': sell_quantity, 'profit': profit, 'title': list_title}

        if buy_updated_time != 0:
            item_data['buy_updated_time'] = buy_updated_time

        if sell_updated_time != 0:
            item_data['sell_updated_time'] = sell_updated_time

        update_item_log(item_log, item, buying, selling, buy_updated_time, sell_updated_time)

        data_list.append(item_data)

    write_item_log(item_log)
    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)
    data = {'base_url': get_base_url(), 'item_data': {}, 'result_list': json.dumps(data_list),
            'result_type': 'frontpage'}
    return render(request, 'grand_exchange.html', data)


def item_string_search(request):
    if 'search_value' not in request.GET:
        data = {'success': False, 'error_id': 1, 'error_msg:': 'Data not set'}
        return HttpResponse(json.dumps(data), 'application/json')

    search_value = request.GET['search_value']
    data_list = []

    item_json = rs_item_json()

    for key, item in item_json.iteritems():
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


def item_id_search(request, item_id):
    item_json = rs_item_json()[item_id]

    data = {'base_url': get_base_url(), 'item_data': json.dumps(item_json), 'result_list': {},
            'keyword': item_json['name'], 'title': item_json['name']}
    return render(request, 'grand_exchange.html', data)


def item_price(request):
    if 'item_id' not in request.GET:
        data = {'success': False, 'error_id': 1, 'error_msg:': 'Data not set', 'data': request.GET}
        return HttpResponse(json.dumps(data), 'application/json')

    item_id = str(request.GET['item_id'])

    item_log = item_log_json()
    updated_buy_price = 0
    updated_sell_price = 0

    urls = [
        'http://services.runescape.com/m=itemdb_oldschool/api/graph/' + item_id + '.json',
        'http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + item_id
    ]

    responses = grequests.map(grequests.get(u) for u in urls)

    try:
        rsbuddy_price = responses[1].json()
        buying = rsbuddy_price['buying']
        selling = rsbuddy_price['selling']
        buy_quantity = rsbuddy_price['buyingQuantity']
        sell_quantity = rsbuddy_price['sellingQuantity']

        if buying == 0:
            updated_data = ge_price_updater(item_log, item_id, 'buyingPrice', False)
            buying = updated_data[0]
            updated_buy_price = updated_data[1]

        if selling == 0:
            updated_data = ge_price_updater(item_log, item_id, 'sellingPrice', False)
            selling = updated_data[0]
            updated_sell_price = updated_data[1]

    except:
        item_log_item = item_log[item_id]
        buy_quantity = 0
        sell_quantity = 0

        if item_log_item['success']:
            buying = item_log_item['buying']
            selling = item_log_item['selling']
            updated_buy_price = item_log_item['buy_price_ts']
            updated_sell_price = item_log_item['sell_price_ts']
        else:
            buying = 0
            selling = 0

    osrs_price_graph = responses[0].json()['daily']
    osrs_price_array = sorted(osrs_price_graph)

    current_price = osrs_price_graph[osrs_price_array[-1]]
    previous_price = osrs_price_graph[osrs_price_array[-2]]

    margin = current_price - previous_price
    margin_ratio = round(100.0 * margin/current_price, 1)
    profit_margin = buying - selling

    item_data = {'selling': selling, 'buying': buying, 'buy_quantity': buy_quantity, 'sell_quantity': sell_quantity,
                 'current_price': current_price, 'previous_price': previous_price, 'margin': margin,
                 'margin_ratio': margin_ratio, 'profit_margin': profit_margin}

    if updated_buy_price != 0:
        item_data['updated_buy_price'] = updated_buy_price

    if updated_sell_price != 0:
        item_data['updated_sell_price'] = updated_sell_price

    update_item_log(item_log, item_id, buying, selling, updated_buy_price, updated_sell_price)
    write_item_log(item_log)

    return render_json(item_data)


def decant_potions(request):
    item_json = rs_item_json()
    item_log = item_log_json()

    potion_list = decant_list

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in potion_list]

    data_list = []

    responses = grequests.map(grequests.get(u) for u in urls)

    for i in xrange(0, 148, 4):
        two_dose = i + 1
        three_dose = i + 2
        four_dose = i + 3

        one_dose_updated_time = 0
        two_dose_updated_time = 0
        three_dose_updated_time = 0
        four_dose_updated_time = 0

        one_dose_id = potion_list[i]
        two_dose_id = potion_list[two_dose]
        three_dose_id = potion_list[three_dose]
        four_dose_id = potion_list[four_dose]

        one_dose_response = responses[i]
        two_dose_response = responses[two_dose]
        three_dose_response = responses[three_dose]
        four_dose_response = responses[four_dose]

        try:
            one_dose_price = one_dose_response.json()['selling']
        except:
            item_log_data = access_item_log(one_dose_id)
            one_dose_price = item_log_data['selling']
            one_dose_updated_time = item_log_data['sell_price_ts']

        try:
            two_dose_price = two_dose_response.json()['selling']
        except:
            item_log_data = access_item_log(two_dose_id)
            two_dose_price = item_log_data['selling']
            two_dose_updated_time = item_log_data['sell_price_ts']

        try:
            three_dose_price = three_dose_response.json()['selling']
        except:
            item_log_data = access_item_log(three_dose_id)
            three_dose_price = item_log_data['selling']
            three_dose_updated_time = item_log_data['sell_price_ts']

        try:
            four_dose_price = four_dose_response.json()['buying']
        except:
            item_log_data = access_item_log(four_dose_id)
            four_dose_price = item_log_data['buying']
            four_dose_updated_time = item_log_data['buy_price_ts']

        four_dose_item_json = item_json[four_dose_id]

        if one_dose_price == 0:
            updated_data = ge_price_updater(item_log, one_dose_id, 'sellingPrice', False)
            one_dose_price = updated_data[0]
            one_dose_updated_time = updated_data[1]

        if two_dose_price == 0:
            updated_data = ge_price_updater(item_log, two_dose_id, 'sellingPrice', False)
            two_dose_price = updated_data[0]
            two_dose_updated_time = updated_data[1]

        if three_dose_price == 0:
            updated_data = ge_price_updater(item_log, three_dose_id, 'sellingPrice', False)
            three_dose_price = updated_data[0]
            three_dose_updated_time = updated_data[1]

        if four_dose_price == 0:
            updated_data = ge_price_updater(item_log, four_dose_id, 'buyingPrice', False)
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

        item_data = {'name': four_dose_item_json['name'].replace('(4)', ''), 'cheapest_cost': cheapest_cost,
            'limit': four_dose_item_json['limit'], 'file_name': four_dose_item_json['file_name'],
            'potion_id': four_dose_item_json['id'], 'one_dose_cost': one_dose_price, 'two_dose_cost': two_dose_price,
            'three_dose_cost': three_dose_price, 'four_dose_cost': four_dose_price, 'profit': profit,
            'cheapest_dose': cheapest_dose}

        if one_dose_updated_time != 0:
            item_data['one_dose_updated_time'] = one_dose_updated_time

        if two_dose_updated_time != 0:
            item_data['two_dose_updated_time'] = two_dose_updated_time

        if three_dose_updated_time != 0:
            item_data['three_dose_updated_time'] = three_dose_updated_time

        if four_dose_updated_time != 0:
            item_data['four_dose_updated_time'] = four_dose_updated_time

        update_item_log(item_log, one_dose_id, 0, one_dose_price, 0, one_dose_updated_time)
        update_item_log(item_log, two_dose_id, 0, two_dose_price, 0, two_dose_updated_time)
        update_item_log(item_log, three_dose_id, 0, three_dose_price, 0, three_dose_updated_time)
        update_item_log(item_log, four_dose_id, four_dose_price, 0, four_dose_updated_time, 0)

        data_list.append(item_data)

    write_item_log(item_log)
    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)
    data = {'base_url': get_base_url(), 'item_data': {}, 'result_list': json.dumps(data_list),
            'result_type': 'decant-potions', 'title': 'Decant Potions'}
    return render(request, 'grand_exchange.html', data)


def clean_herbs(request):
    item_json = rs_item_json()
    item_log = item_log_json()

    herblore_list = clean_herb_list

    requirements = [3, 5, 11, 20, 25, 30, 40, 48, 54, 59, 65, 67, 70, 75]

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in herblore_list]

    data_list = []

    responses = grequests.map(grequests.get(u) for u in urls)

    for i in xrange(0, 28, 2):
        clean = i + 1

        grimy_item_json = item_json[herblore_list[i]]
        clean_item_json = item_json[herblore_list[clean]]
        grimy_response = responses[i]
        clean_response = responses[clean]
        grimy_id = herblore_list[i]
        clean_id = herblore_list[clean]
        grimy_updated_time = 0
        clean_updated_time = 0

        try:
            grimy_cost = grimy_response.json()['selling']
        except:
            item_log_data = access_item_log(grimy_id)
            grimy_cost = item_log_data['selling']
            grimy_updated_time = item_log_data['sell_price_ts']

        try:
            clean_sale = clean_response.json()['buying']
        except:
            item_log_data = access_item_log(clean_id)
            clean_sale = item_log_data['buying']
            clean_updated_time = item_log_data['buy_price_ts']

        if grimy_cost == 0:
            updated_data = ge_price_updater(item_log, grimy_id, 'sellingPrice', False)
            grimy_cost = updated_data[0]
            grimy_updated_time = updated_data[1]

        if clean_sale == 0:
            updated_data = ge_price_updater(item_log, clean_id, 'buyingPrice', False)
            clean_sale = updated_data[0]
            clean_updated_time = updated_data[1]

        profit = clean_sale - grimy_cost

        item_data = {'clean_file_name': clean_item_json['file_name'], 'grimy_buy_limit': grimy_item_json['limit'],
            'grimy_file_name': grimy_item_json['file_name'], 'name': clean_item_json['name'],
            'grimy_id': grimy_id, 'clean_id': clean_id, 'grimy_cost': grimy_cost, 'clean_sale': clean_sale,
            'profit': profit, 'requirement': requirements[i / 2], 'grimy_name': grimy_item_json['name']}

        if grimy_updated_time != 0:
            item_data['grimy_updated_time'] = grimy_updated_time

        if clean_updated_time != 0:
            item_data['clean_updated_time'] = clean_updated_time

        data_list.append(item_data)

        update_item_log(item_log, grimy_id, 0, grimy_cost, 0, grimy_updated_time)
        update_item_log(item_log, clean_id, clean_sale, 0, clean_updated_time, 0)

    write_item_log(item_log)
    data = {'base_url': get_base_url(), 'item_data': {}, 'result_list': json.dumps(data_list),
            'result_type': 'clean-herbs', 'title': 'Clean Herbs'}
    return render(request, 'grand_exchange.html', data)


def barrows_repair(request):
    item_json = rs_item_json()
    item_log = item_log_json()

    barrows_list = barrows_repair_list

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in barrows_list]

    weapon_repair = 100000
    helmet_repair = 60000
    body_repair = 90000
    leg_repair = 80000
    smithing_level = 0

    if 'smithing_level' in request.GET:
        smithing_level = int(request.GET['smithing_level'])
        if smithing_level > 0:
            ratio = 1 - (smithing_level / 200.0)
            weapon_repair = int(ratio * weapon_repair)
            helmet_repair = int(ratio * helmet_repair)
            body_repair = int(ratio * body_repair)
            leg_repair = int(ratio * leg_repair)

    responses = grequests.map(grequests.get(u) for u in urls)

    data_list = []

    for i in xrange(0, 40, 2):
        broken = i + 1

        fixed_item_json = item_json[barrows_list[i]]
        broken_item_json = item_json[barrows_list[broken]]
        fixed_item_id = barrows_list[i]
        broken_item_id = barrows_list[broken]
        broken_updated_time = 0
        fixed_updated_time = 0

        broken_response = responses[broken]
        fixed_response = responses[i]

        try:
            broken_cost = broken_response.json()['selling']
        except:
            item_log_data = access_item_log(broken_item_id)
            broken_cost = item_log_data['selling']
            broken_updated_time = item_log_data['sell_price_ts']

        try:
            fixed_sale = fixed_response.json()['buying']
        except:
            item_log_data = access_item_log(fixed_item_id)
            fixed_sale = item_log_data['buying']
            fixed_updated_time = item_log_data['buy_price_ts']

        if broken % 8 == 1:
            repair_cost = weapon_repair
        elif broken % 8 == 3:
            repair_cost = helmet_repair
        elif broken % 8 == 5:
            repair_cost = body_repair
        elif broken % 8 == 7:
            repair_cost = leg_repair

        if broken_cost == 0:
            updated_data = ge_price_updater(item_log, broken_item_id, 'sellingPrice', False)
            broken_cost = updated_data[0]
            broken_updated_time = updated_data[1]

        if fixed_sale == 0:
            updated_data = ge_price_updater(item_log, fixed_item_id, 'buyingPrice', False)
            broken_cost = updated_data[0]
            broken_updated_time = updated_data[1]

        profit = fixed_sale - (broken_cost + repair_cost)

        item_data = {'fixed_file_name': fixed_item_json['file_name'], 'broken_buy_limit': fixed_item_json['limit'],
            'broken_file_name': broken_item_json['file_name'], 'name': fixed_item_json['name'],
            'fixed_id': fixed_item_id, 'broken_id': broken_item_id, 'broken_name': broken_item_json['name'],
            'broken_cost': broken_cost, 'fixed_sale': fixed_sale, 'profit': profit, 'repair': repair_cost,
            'smithing_level': smithing_level}

        if broken_updated_time != 0:
            item_data['broken_updated_time'] = broken_updated_time

        if fixed_updated_time != 0:
            item_data['fixed_updated_time'] = fixed_updated_time

        update_item_log(item_log, broken_item_id, 0, broken_cost, 0, broken_updated_time)
        update_item_log(item_log, fixed_item_id, fixed_sale, 0, fixed_updated_time, 0)

        data_list.append(item_data)

    write_item_log(item_log)
    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)
    data = {'base_url': get_base_url(), 'item_data': {}, 'result_list': json.dumps(data_list),
            'result_type': 'barrows-repair', 'title': 'Barrows Repair'}
    return render(request, 'grand_exchange.html', data)


def potion_making(request):
    item_json = rs_item_json()
    item_log = item_log_json()

    item_list = potion_making_list

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in item_list]

    responses = grequests.map(grequests.get(u) for u in urls)
    data_list = []
    response_dict = {}

    for i, item in enumerate(item_list):
        response = responses[i]
        try:
            json_response = response.json()
            update_item_log(item_log, item, json_response['buying'], json_response['selling'], 0, 0)
            response_dict[item] = json_response
        except:
            json_response = access_item_log(item)
            update_item_log(item_log, item, json_response['buying'], json_response['selling'], json_response['buy_price_ts'], json_response['sell_price_ts'])
            response_dict[item] = json_response

    potion_dict = potion_making_dict

    vial_of_water_cost = response_dict['227']['selling']
    vial_of_water_updated_time = 0

    if vial_of_water_cost == 0:
        updated_data = ge_price_updater(item_log, 227, 'sellingPrice', False)
        vial_of_water_cost = updated_data[0]
        vial_of_water_updated_time = updated_data[1]

    for pot in potion_dict:
        potion = pot['potion']
        potion_item_json = item_json[potion]
        potion_response = response_dict[potion]
        potion_sale = potion_response['buying']
        ingredients = pot['ingredients']
        ingredient_list = []

        if 'buy_price_ts' in potion_response:
            potion_updated_time = potion_response['buy_price_ts']
        else:
            potion_updated_time = 0

        total_cost = vial_of_water_cost

        for i, ingredient in enumerate(ingredients):
            ingredient_json = item_json[ingredient]
            ingredient_response = response_dict[ingredient]
            buy_price = ingredient_response['selling']

            if 'sell_price_ts' in ingredient_response:
                ingredient_updated_time = ingredient_response['sell_price_ts']
            else:
                ingredient_updated_time = 0

            if buy_price == 0:
                updated_data = ge_price_updater(item_log, ingredient, 'sellingPrice', False)
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

            if ingredient_updated_time != 0:
                ingredient_dict['ingredient_updated_time'] = ingredient_updated_time

            update_item_log(item_log, ingredient, 0, buy_price, 0, ingredient_updated_time)

            ingredient_list.append(ingredient_dict)

        if potion_sale == 0:
            updated_data = ge_price_updater(item_log, potion, 'buyingPrice', False)
            potion_sale = updated_data[0]
            potion_updated_time = updated_data[1]

        profit = potion_sale - total_cost

        item_data = {'file_name': potion_item_json['file_name'], 'limit': potion_item_json['limit'],
                     'name': potion_item_json['name'].replace('(3)', ''), 'id': potion, 'total_cost': total_cost,
                     'ingredient_list': ingredient_list, 'vial_of_water_cost': vial_of_water_cost,
                     'potion_sale': potion_sale, 'profit': profit}

        if potion_updated_time != 0:
            item_data['potion_updated_time'] = potion_updated_time

        update_item_log(item_log, potion, potion_sale, 0, potion_updated_time, 0)
        data_list.append(item_data)

    write_item_log(item_log)
    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)
    data = {'base_url': get_base_url(), 'item_data': {}, 'result_list': json.dumps(data_list),
            'result_type': 'potion-making', 'title': 'Potion Making'}
    return render(request, 'grand_exchange.html', data)


def unfinished_potions(request):
    item_json = rs_item_json()
    item_log = item_log_json()

    potion_list = unfinished_potion_list

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in potion_list]

    data_list = []

    responses = grequests.map(grequests.get(u) for u in urls)

    vial_of_water_cost = responses[0].json()['selling']
    vial_of_water_updated_time = 0

    if vial_of_water_cost == 0:
        updated_data = ge_price_updater(item_log, 227, 'sellingPrice', False)
        vial_of_water_cost = updated_data[0]
        vial_of_water_updated_time = updated_data[1]

    for i in xrange(1, 29, 2):
        potion = i + 1

        herb_item_json = item_json[potion_list[i]]
        potion_item_json = item_json[potion_list[potion]]
        herb_response = responses[i]
        potion_response = responses[potion]

        herb_id = potion_list[i]
        potion_id = potion_list[potion]
        herb_updated_time = 0
        potion_updated_time = 0

        try:
            herb_cost = herb_response.json()['selling']
        except:
            item_log_data = access_item_log(herb_id)
            herb_cost = item_log_data['selling']
            herb_updated_time = item_log_data['sell_price_ts']

        try:
            potion_sale = potion_response.json()['buying']
        except:
            item_log_data = access_item_log(potion_id)
            potion_sale = item_log_data['buying']
            potion_updated_time = item_log_data['buy_price_ts']

        if herb_cost == 0:
            updated_data = ge_price_updater(item_log, herb_id, 'sellingPrice', False)
            herb_cost = updated_data[0]
            herb_updated_time = updated_data[1]

        if potion_sale == 0:
            updated_data = ge_price_updater(item_log, potion_id, 'buyingPrice', False)
            potion_sale = updated_data[0]
            potion_updated_time = updated_data[1]

        profit = potion_sale - (vial_of_water_cost + herb_cost)

        item_data = {'herb_file_name': herb_item_json['file_name'], 'limit': herb_item_json['limit'],
            'potion_file_name': potion_item_json['file_name'], 'name': potion_item_json['name'],
            'herb_id': herb_id, 'potion_id': potion_id, 'herb_cost': herb_cost, 'potion_sale': potion_sale,
            'profit': profit, 'vial_of_water_cost': vial_of_water_cost, 'herb_name':  herb_item_json['name']}

        if herb_updated_time != 0:
            item_data['herb_updated_time'] = herb_updated_time

        if potion_updated_time != 0:
            item_data['potion_updated_time'] = potion_updated_time

        update_item_log(item_log, herb_id, 0, herb_cost, 0, herb_updated_time)
        update_item_log(item_log, potion_id, potion_sale, 0, potion_updated_time, 0)

        data_list.append(item_data)

    write_item_log(item_log)
    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)
    data = {'base_url': get_base_url(), 'item_data': {}, 'result_list': json.dumps(data_list),
            'result_type': 'unfinished-potions', 'title': 'Unfinished Potions'}
    return render(request, 'grand_exchange.html', data)


def plank_making(request):
    item_json = rs_item_json()
    item_log = item_log_json()

    data_list = []
    plank_making_list = ['1511', '960', '1521', '8778', '6333', '8780', '6332', '8782']
    sawmill_cost_list = [100, 250, 500, 1500]
    type_list = ['Regular', 'Oak', 'Teak', 'Mahogany']

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in plank_making_list]
    responses = grequests.map(grequests.get(u) for u in urls)

    for i in xrange(0, 8, 2):
        plank = i + 1

        log_item_json = item_json[plank_making_list[i]]
        plank_item_json = item_json[plank_making_list[plank]]

        sawmill_cost = sawmill_cost_list[i / 2]
        plank_type = type_list[i / 2]
        log_id = plank_making_list[i]
        plank_id = plank_making_list[plank]
        log_updated_time = 0
        plank_updated_time = 0
        log_response = responses[i]
        plank_response = responses[plank]

        try:
            log_cost = log_response.json()['selling']
        except:
            item_log_data = access_item_log(log_id)
            log_cost = item_log_data['selling']
            log_updated_time = item_log_data['sell_price_ts']

        try:
            plank_sale = plank_response.json()['buying']
        except:
            item_log_data = access_item_log(plank_id)
            plank_sale = item_log_data['buying']
            plank_updated_time = item_log_data['buy_price_ts']

        if log_cost == 0:
            updated_data = ge_price_updater(item_log, log_id, 'sellingPrice', False)
            log_cost = updated_data[0]
            log_updated_time = updated_data[1]

        if plank_sale == 0:
            updated_data = ge_price_updater(item_log, plank_id, 'buyingPrice', False)
            plank_sale = updated_data[0]
            plank_updated_time = updated_data[1]

        total_cost = log_cost + sawmill_cost
        profit = plank_sale - total_cost

        item_data = {'log_file_name': log_item_json['file_name'], 'limit': log_item_json['limit'],
            'plank_file_name': plank_item_json['file_name'], 'log_name': log_item_json['name'],
            'log_id': log_id, 'plank_id': plank_id, 'log_cost': log_cost, 'plank_sale': plank_sale,
            'profit': profit, 'sawmill_cost': sawmill_cost, 'total_cost': total_cost,
            'plank_name': plank_item_json['name'], 'plank_type': plank_type}

        if log_updated_time != 0:
            item_data['log_updated_time'] = log_updated_time

        if plank_updated_time != 0:
            item_data['plank_updated_time'] = plank_updated_time

        update_item_log(item_log, log_id, 0, log_cost, 0, log_updated_time)
        update_item_log(item_log, plank_id, plank_sale, 0, plank_updated_time, 0)

        data_list.append(item_data)

    write_item_log(item_log)
    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)
    data = {'base_url': get_base_url(), 'item_data': {}, 'result_list': json.dumps(data_list),
            'result_type': 'plank-making', 'title': 'Plank Making'}
    return render(request, 'grand_exchange.html', data)


def tan_leather(request):
    item_json = rs_item_json()
    item_log = item_log_json()

    data_list = []
    tanning_list = ['1739', '1741', '1739', '1743', '1753', '1745', '1751', '2505', '1749', '2507', '1747', '2509']
    al_kharid_cost_list = [1, 3, 20, 20, 20, 20]
    canifis_cost_list = [2, 5, 45, 45, 45, 45]

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in tanning_list]
    responses = grequests.map(grequests.get(u) for u in urls)

    for i in xrange(0, 12, 2):
        leather = i + 1

        hide_item_json = item_json[tanning_list[i]]
        leather_item_json = item_json[tanning_list[leather]]

        al_kharid_cost = al_kharid_cost_list[i / 2]
        canifis_cost = canifis_cost_list[i / 2]
        hide_response = responses[i]
        leather_response = responses[leather]
        hide_id = tanning_list[i]
        leather_id = tanning_list[leather]
        hide_updated_time = 0
        leather_updated_time = 0

        try:
            hide_cost = hide_response.json()['selling']
        except:
            item_log_data = access_item_log(hide_id)
            hide_cost = item_log_data['selling']
            hide_updated_time = item_log_data['sell_price_ts']

        try:
            leather_sale = leather_response.json()['buying']
        except:
            item_log_data = access_item_log(leather_id)
            leather_sale = item_log_data['buying']
            leather_updated_time = item_log_data['buy_price_ts']

        if hide_cost == 0:
            updated_data = ge_price_updater(item_log, hide_id, 'sellingPrice', False)
            hide_cost = updated_data[0]
            hide_updated_time = updated_data[1]

        if leather_sale == 0:
            updated_data = ge_price_updater(item_log, leather_id, 'buyingPrice', False)
            leather_sale = updated_data[0]
            leather_updated_time = updated_data[1]

        total_cost = hide_cost + al_kharid_cost
        profit = leather_sale - total_cost

        item_data = {'hide_file_name': hide_item_json['file_name'], 'limit': hide_item_json['limit'],
            'leather_file_name': leather_item_json['file_name'], 'hide_name': hide_item_json['name'],
            'hide_id': hide_id, 'leather_id': leather_id, 'hide_cost': hide_cost, 'leather_sale': leather_sale,
            'profit': profit, 'al_kharid_cost': al_kharid_cost, 'total_cost': total_cost,
            'leather_name': leather_item_json['name'], 'canifis_cost': canifis_cost}

        if hide_updated_time != 0:
            item_data['hide_updated_time'] = hide_updated_time

        if leather_updated_time != 0:
            item_data['leather_updated_time'] = leather_updated_time

        update_item_log(item_log, hide_id, 0, hide_cost, 0, hide_updated_time)
        update_item_log(item_log, leather_id, leather_sale, 0, leather_updated_time, 0)

        data_list.append(item_data)

    write_item_log(item_log)
    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)
    data = {'base_url': get_base_url(), 'item_data': {}, 'result_list': json.dumps(data_list),
            'result_type': 'tan-leather', 'title': 'Tan Leather'}
    return render(request, 'grand_exchange.html', data)


def enchant_bolts(request):
    item_json = rs_item_json()
    item_log = item_log_json()

    enchant_list = enchanted_list

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in enchant_list]

    responses = grequests.map(grequests.get(u) for u in urls)
    data_list = []
    response_dict = {}

    for i, item in enumerate(enchant_list):
        response = responses[i]
        try:
            json_response = response.json()
            update_item_log(item_log, item, json_response['buying'], json_response['selling'], 0, 0)
            response_dict[item] = json_response
        except:
            json_response = access_item_log(item)
            update_item_log(item_log, item, json_response['buying'], json_response['selling'], json_response['buy_price_ts'], json_response['sell_price_ts'])
            response_dict[item] = json_response

    enchant_dict = enchanted_dict

    for enchant in enchant_dict:
        bolt = enchant['bolt']
        staff = enchant['staff']
        bolt_item_json = item_json[bolt]
        staff_item_json = item_json[staff]
        bolt_response = response_dict[bolt]
        bolt_sale = bolt_response['buying']
        required = enchant['required']
        required_list = []

        if 'buy_price_ts' in bolt_response:
            bolt_updated_time = bolt_response['buy_price_ts']
        else:
            bolt_updated_time = 0

        total_cost = 0

        for i, item in enumerate(required):
            required_json = item_json[item]
            required_response = response_dict[item]
            buy_price = required_response['selling']

            if 'sell_price_ts' in required_response:
                required_updated_time = required_response['sell_price_ts']
            else:
                required_updated_time = 0

            if buy_price == 0:
                updated_data = ge_price_updater(item_log, item, 'sellingPrice', False)
                buy_price = updated_data[0]
                required_updated_time = updated_data[1]

            required_dict = {'id': item, 'name': required_json['name'], 'limit': required_json['limit'],
                               'file_name': required_json['file_name'], 'buy_price': buy_price}

            if 'multiples' in enchant:
                multiple = enchant['multiples'][i]
                total_cost = total_cost + (buy_price*multiple)
                if multiple > 1:
                    required_dict['multiple'] = {}
                    required_dict['multiple'][item] = multiple
            else:
                total_cost = total_cost + buy_price

            if required_updated_time != 0:
                required_dict['required_updated_time'] = required_updated_time

            required_list.append(required_dict)

        if bolt_sale == 0:
            updated_data = ge_price_updater(item_log, bolt, 'buyingPrice', False)
            bolt_sale = updated_data[0]
            bolt_updated_time = updated_data[1]

        profit = (bolt_sale * 10) - total_cost

        item_data = {'file_name': bolt_item_json['file_name'], 'limit': bolt_item_json['limit'],
                     'name': bolt_item_json['name'], 'id': bolt, 'total_cost': total_cost, 'staff_id': staff,
                     'required_list': required_list, 'bolt_sale': bolt_sale, 'magic_level': enchant['magic_level'],
                     'staff_file_name': staff_item_json['file_name'], 'staff_name': staff_item_json['name'],
                     'profit': profit}

        if bolt_updated_time != 0:
            item_data['bolt_updated_time'] = bolt_updated_time

        data_list.append(item_data)

    write_item_log(item_log)
    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)
    data = {'base_url': get_base_url(), 'item_data': {}, 'result_list': json.dumps(data_list),
            'result_type': 'enchant-bolts', 'title': 'Enchant Bolts'}
    return render(request, 'grand_exchange.html', data)


def item_sets(request):
    item_json = rs_item_json()
    item_log = item_log_json()

    armour_list = item_set_list

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in armour_list]

    responses = grequests.map(grequests.get(u) for u in urls)
    data_list = []
    response_dict = {}

    for i, item in enumerate(armour_list):
        response = responses[i]
        try:
            json_response = response.json()
            update_item_log(item_log, item, json_response['buying'], json_response['selling'], 0, 0)
            response_dict[item] = json_response
        except:
            json_response = access_item_log(item)
            update_item_log(item_log, item, json_response['buying'], json_response['selling'], json_response['buy_price_ts'], json_response['sell_price_ts'])
            response_dict[item] = json_response

    armor_set_dict = item_set_dict

    for armor_set in armor_set_dict:
        set_batch = armor_set['set']
        set_json = item_json[set_batch]
        set_response = response_dict[set_batch]
        set_sale = response_dict[set_batch]['buying']
        items = armor_set['items']
        item_list = []

        if 'buy_price_ts' in set_response:
            set_updated_time = set_response['buy_price_ts']
        else:
            set_updated_time = 0

        total_cost = 0

        for i, item in enumerate(items):
            set_item_json = item_json[item]
            set_item_response = response_dict[item]
            buy_price = set_item_response['selling']

            if 'sell_price_ts' in set_item_response:
                item_updated_time = set_item_response['sell_price_ts']
            else:
                item_updated_time = 0

            if buy_price == 0:
                updated_data = ge_price_updater(item_log, item, 'sellingPrice', False)
                buy_price = updated_data[0]
                item_updated_time = updated_data[1]

            item_dict = {'id': item, 'name': set_item_json['name'], 'limit': set_item_json['limit'],
                         'file_name': set_item_json['file_name'], 'buy_price': buy_price}

            total_cost = total_cost + buy_price

            if item_updated_time != 0:
                item_dict['item_updated_time'] = item_updated_time

            item_list.append(item_dict)

        if set_sale == 0:
            updated_data = ge_price_updater(item_log, set_batch, 'buyingPrice', False)
            set_sale = updated_data[0]
            set_updated_time = updated_data[1]

        profit = set_sale - total_cost

        item_data = {'file_name': set_json['file_name'], 'limit': set_json['limit'],
                     'name': set_json['name'], 'id': set_batch, 'total_cost': total_cost,
                     'item_list': item_list, 'set_sale': set_sale, 'profit': profit}

        if set_updated_time != 0:
            item_data['set_updated_time'] = set_updated_time

        data_list.append(item_data)

    write_item_log(item_log)
    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)
    data = {'base_url': get_base_url(), 'item_data': {}, 'result_list': json.dumps(data_list),
            'result_type': 'item-sets', 'title': 'Item Sets'}
    return render(request, 'grand_exchange.html', data)


def magic_tablets(request):
    item_json = rs_item_json()
    item_log = item_log_json()

    item_list = magic_tablet_list

    urls = ['http://api.rsbuddy.com/grandExchange?a=guidePrice&i=' + i for i in item_list]

    responses = grequests.map(grequests.get(u) for u in urls)
    data_list = []
    response_dict = {}

    for i, item in enumerate(item_list):
        response = responses[i]
        try:
            json_response = response.json()
            update_item_log(item_log, item, json_response['buying'], json_response['selling'], 0, 0)
            response_dict[item] = json_response
        except:
            json_response = access_item_log(item)
            update_item_log(item_log, item, json_response['buying'], json_response['selling'], json_response['buy_price_ts'], json_response['sell_price_ts'])
            response_dict[item] = json_response

    tablet_dict = [
        {'magic_level': 25, 'items': ['563'], 'tablet': '8007', 'staff': '11998'}, #Varrock teleport: Law rune, 3 Air runes, Fire rune, Soft clay
        {'magic_level': 31, 'items': ['563'], 'tablet': '8008', 'staff': '20736'}, #Lumbridge teleport: Law rune, 3 Air runes, Earth rune, Soft clay
        {'magic_level': 37, 'items': ['563'], 'tablet': '8009', 'staff': '20730'}, #Falador teleport: Law rune, 3 Air runes, Water rune, Soft clay
        {'magic_level': 40, 'items': ['563'], 'tablet': '8013', 'staff': '20736'}, #Teleport to house: Law rune, Air rune, Earth rune, soft clay
        {'magic_level': 45, 'items': ['563'], 'tablet': '8010', 'staff': '1381'}, #Camelot teleport: Law rune, 5 Air runes, Soft clay
        {'magic_level': 51, 'items': ['563'], 'tablet': '8011', 'staff': '1383', 'multiple': [2]}, #Ardougne teleport: 2 Law rune, 2 Water runes, Soft clay
        {'magic_level': 58, 'items': ['563'], 'tablet': '8012', 'staff': '1385', 'multiple': [2]}, #Watchtower teleport: 2 Law runes, 2 Earth runes, Soft clay

        {'magic_level': 7, 'items': ['564'], 'tablet': '8016', 'staff': '1383'}, #Enchant sapphire: 1 cosmic rune, 1 water rune, 1 soft clay
        {'magic_level': 27, 'items': ['564'], 'tablet': '8017', 'staff': '1381'}, #Enchant emerald: 1 cosmic rune, 3 air runes, 1 soft clay
        {'magic_level': 49, 'items': ['564'], 'tablet': '8018', 'staff': '1387'}, #Enchant ruby: 1 cosmic rune, 5 fire runes, 1 soft clay
        {'magic_level': 57, 'items': ['564'], 'tablet': '8019', 'staff': '1385'}, #Enchant diamond: 1 cosmic rune, 10 earth runes, 1 soft clay
        {'magic_level': 68, 'items': ['564'], 'tablet': '8020', 'staff': '6562'}, #Enchant dragonstone: 1 cosmic rune, 15 earth runes, 15 water runes, 1 soft clay
        {'magic_level': 87, 'items': ['564'], 'tablet': '8021', 'staff': '3053'}, #Enchant onyx: 1 cosmic rune, 20 earth runes, 20 fire runes, and 1 soft clay

        {'magic_level': 6, 'items': ['563'], 'tablet': '19613', 'staff': '1385'}, #Lumbridge graveyard teleport: 1 Law rune, 2 earth runes, Dark essence block
        {'magic_level': 17, 'items': ['563'], 'tablet': '19615', 'staff': '6562'}, #Draynor manor teleport: 1 law rune, 1 earth rune, 1 water rune, Dark essence block
        {'magic_level': 28, 'items': ['563', '558'], 'tablet': '19617', 'multiple': [1, 2]}, #Mind altar teleport: 1 law rune, 2 mind runes, Dark essence block
        {'magic_level': 40, 'items': ['563', '566'], 'tablet': '19619', 'multiple': [1, 2]}, #Salve graveyard teleport: 1 law rune, 2 soul runes, Dark essence block
        {'magic_level': 48, 'items': ['563', '566'], 'tablet': '19621', 'staff': '1385'}, #Fenkenstrain's castle teleport: 1 law rune, 1 earth rune, 1 soul rune, Dark essence block
        {'magic_level': 61, 'items': ['563', '566'], 'tablet': '19623', 'multiple': [2, 2]}, #West ardougne teleport: 2 law runes, 2 soul runes, Dark essence block
        {'magic_level': 65, 'items': ['563', '566', '561'], 'tablet': '19625'}, #Harmony island teleport: 1 law rune, 1 soul rune, 1 nature rune, Dark essence block
        {'magic_level': 71, 'items': ['563', '566', '565'], 'tablet': '19627'}, #Cemetery teleport: 1 law rune, 1 soul rune, 1 blood rune, Dark essence block
        {'magic_level': 83, 'items': ['563', '566', '565'], 'tablet': '19629', 'multiple': [2, 2, 1]}, #Barrows teleport: 2 law runes, 2 soul runes, 1 blood rune, Dark essence block
        {'magic_level': 90, 'items': ['563', '566', '565'], 'tablet': '19631', 'multiple': [2, 2, 2]} #Ape atoll teleport: 2 law runes, 2 soul runes, 2 blood runes, Dark essence block
    ]

    soft_clay_cost = response_dict['1761']['selling']
    soft_clay_updated_time = 0

    if soft_clay_cost == 0:
        updated_data = ge_price_updater(1761, 'sellingPrice', False)
        soft_clay_cost = updated_data[0]
        soft_clay_updated_time = updated_data[1]

    for tab in tablet_dict:
        tablet = tab['tablet']
        tablet_item_json = item_json[tablet]
        tablet_response = response_dict[tablet]
        tablet_sale = tablet_response['buying']
        items = tab['items']
        item_list = []

        if 'buy_price_ts' in tablet_response:
            tablet_updated_time = tablet_response['buy_price_ts']
        else:
            tablet_updated_time = 0

        total_cost = soft_clay_cost

        for i, item in enumerate(items):
            req_item_json = item_json[item]
            req_item_response = response_dict[item]
            buy_price = req_item_response['selling']

            if 'sell_price_ts' in tablet_response:
                item_updated_time = tablet_response['sell_price_ts']
            else:
                item_updated_time = 0

            if buy_price == 0:
                updated_data = ge_price_updater(item_log, item, 'sellingPrice', False)
                buy_price = updated_data[0]
                item_updated_time = updated_data[1]

            item_dict = {'id': item, 'file_name': req_item_json['file_name'], 'name': req_item_json['name'],
                        'limit': req_item_json['limit'], 'buy_price': buy_price}

            if 'multiple' in tab:
                multiple = tab['multiple'][i]
                total_cost = total_cost + (buy_price*multiple)
                if multiple > 1:
                    item_dict['multiple'] = {}
                    item_dict['multiple'][item] = multiple
            else:
                total_cost = total_cost + buy_price

            if item_updated_time != 0:
                item_dict['item_updated_time'] = item_updated_time

            item_list.append(item_dict)

        if tablet_sale == 0:
            updated_data = ge_price_updater(item_log, tablet, 'buyingPrice', False)
            tablet_sale = updated_data[0]
            tablet_updated_time = updated_data[1]

        profit = tablet_sale - total_cost

        item_data = {'file_name': tablet_item_json['file_name'], 'limit': tablet_item_json['limit'],
                     'name': tablet_item_json['name'], 'id': tablet, 'total_cost': total_cost,
                     'item_list': item_list, 'soft_clay_cost': soft_clay_cost, 'tablet_sale': tablet_sale,
                     'profit': profit, 'magic_level': tab['magic_level']}

        if 'staff' in tab:
            staff = tab['staff']
            staff_item_json = item_json[staff]

            item_data['staff_id'] = staff
            item_data['staff_name'] = staff_item_json['name']
            item_data['staff_file_name'] = staff_item_json['file_name']

        if tablet_updated_time != 0:
            item_data['tablet_updated_time'] = tablet_updated_time

        data_list.append(item_data)

    write_item_log(item_log)
    data_list = sorted(data_list, key=lambda k: k['profit'], reverse=True)
    data = {'base_url': get_base_url(), 'item_data': {}, 'result_list': json.dumps(data_list),
            'result_type': 'magic-tablets', 'title': 'Magic Tablets'}
    return render(request, 'grand_exchange.html', data)


