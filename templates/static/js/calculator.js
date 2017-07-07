var levels = {
    '1': 0, '2': 83, '3': 174, '4': 276, '5': 388, '6': 512, '7': 650, '8': 801, '9': 969, '10': 1154, '11': 1358,
    '12': 1584, '13': 1833, '14': 2107, '15': 2411, '16': 2746, '17': 3115, '18': 3523, '19': 3973, '20': 4470,
    '21': 5018, '22': 5624, '23': 6291, '24': 7028, '25': 7842, '26': 8740, '27': 9730, '28': 10824, '29': 12031,
    '30': 13363, '31': 14833, '32': 16456, '33': 18247, '34': 20224, '35': 22406, '36': 24815, '37': 27473,
    '38': 30408, '39': 33648, '40': 37224, '41': 41171, '42': 45529, '43': 50339, '44': 55649, '45': 61512,
    '46': 67983, '47': 75127, '48': 83014, '49': 91721, '50': 101333, '51': 111945, '52': 123660, '53': 136594,
    '54': 150872, '55': 166636, '56': 184040, '57': 203254, '58': 224466, '59': 247886, '60': 273742, '61': 302288,
    '62': 333804, '63': 368599, '64': 407015, '65': 449428, '66': 496254, '67': 547953, '68': 605032, '69': 668051,
    '70': 737627, '71': 814445, '72': 899256, '73': 992895, '74': 1096278, '75': 1210421, '76': 1336443, '77': 1475581,
    '78': 1629200, '79': 1798808, '80': 1968068, '81': 2192818, '82': 2421087, '83': 2673114, '84': 2951373,
    '85': 3258594, '86': 3597729, '87': 3972294, '88': 4385776, '89': 4842295, '90': 5346332, '91': 5902831,
    '92': 6517253, '93': 7195629, '94': 7994614, '95': 8771558, '96': 9684577, '97': 10692629, '98': 11805606,
    '99': 13034431
};

function init() {
    $('#calculator_link').addClass('active');

    var $calculator_wrapper = $('#calculator_wrapper');
    var $calculator_template = $(globals.template);

    $calculator_wrapper.append(handlebars_helper(globals.calc_data, $calculator_template));

    if (localStorage.getItem("username") !== null && globals.template == '#combat_calculator_template') {
        fill_combat_highscores(localStorage.getItem("username"), $('#highscore_username'));
    } else if(localStorage.getItem("username") !== null) {
        fill_highscore_level(localStorage.getItem("username"), $('#highscore_username'));
    }

    if(globals.calc_type != '') {
        if(globals.calc_type == 'Prayer') {
            $.when(price_lookup(globals.calc_type)).done(function(response) {
                var $bones = $('.bone');
                var $ensouled = $('.ensouled');

                for (var i = 0; i < $bones.length; i++) {
                    var $current_bone = $($bones[i]);
                    var bone_id = $current_bone.attr('data-id');
                    var bone_exp = parseFloat($current_bone.find('.exp').text());
                    var bone_selling = parseInt(response[bone_id]['selling']);
                    var bone_amount = parseInt($current_bone.find('.amount').text());

                    $current_bone.attr('data-selling', bone_selling);
                    $current_bone.find('.gp_per_exp').text(-(Math.round(100*(bone_selling/bone_exp))/100));
                    $current_bone.find('.profit').text(number_comma_format(-(bone_amount*bone_selling)));
                }

                for (var h = 0; h < $ensouled.length; h++) {
                    var $current_ensouled = $($ensouled[h]);
                    var ensouled_id = $current_ensouled.attr('data-id');
                    var ensouled_exp = $current_ensouled.attr('data-exp');
                    var ensouled_amount = parseInt($current_ensouled.find('.amount').text());
                    var ensouled_selling = parseInt(response[ensouled_id]['selling']);
                    var $content = $current_ensouled.find('.content');

                    for (var f = 0; f < $content.length; f++) {
                        var $current_content = $($content[f]);
                        var multiple = parseInt($current_content.attr('data-multiple'));
                        ensouled_selling = ensouled_selling + (parseInt(response[$current_content.attr('data-id')]['selling'])*multiple);
                    }

                    $current_ensouled.attr('data-selling', ensouled_selling);
                    $current_ensouled.find('.gp_per_exp').text(-(Math.round(100*(ensouled_selling/ensouled_exp))/100));
                    $current_ensouled.find('.profit').text(number_comma_format(-(ensouled_amount*ensouled_selling)));
                }
            });
        }
    }
}

function highscore_lookup(username, highscore_type) {
    return $.ajax ({
        url: globals.base_url + '/calculator/highscore',
        data: {'username': username, 'type': highscore_type},
        dataType: 'json',
        type: "GET"
    });
}

function price_lookup(calc_type) {
    return $.ajax ({
        url: globals.base_url + '/calculator/prices',
        data: {'calc_type': calc_type},
        dataType: 'json',
        type: "GET"
    });
}

function calculate_combat(hitpoints, attack, strength, defence, magic, ranged, prayer) {
    var base = 0.25*(defence + hitpoints + Math.floor(prayer/2));
    var melee = 0.325*(attack + strength);
    var range = 0.325*(Math.floor(ranged*1.5));
    var mage = 0.325*(Math.floor(magic*1.5));
    var max = Math.max(melee, range, mage);

    var combat = base + max;

    $('#combat_level').text(Math.round(combat*100)/100);

    var next_level = Math.floor(combat) + 1;

    var melee_levels = number_of_levels(combat, 0.325);
    var base_levels = number_of_levels(combat, 0.25);
    var prayer_levels = number_of_levels(combat, 0.125);
    var range_levels = number_of_level_rm(ranged, base);
    var magic_levels = number_of_level_rm(magic, base);

    function number_of_levels(combat_level, add) {
        var levels = 0;
        while(combat_level < next_level) {
            combat_level += add;
            ++levels;
        }
        return levels;
    }

    function number_of_level_rm(current_level, base_combat) {
        var levels = 0;
        var calc = Math.floor(current_level * 1.5) * 0.325;
        while((calc + base_combat) < next_level) {
            calc = Math.floor((current_level + ++levels) * 1.5) * 0.325;
        }
        return levels;
    }

    if(prayer_levels % 2 == 0){
        ++prayer_levels;
    }

    var next_level_data = { 'combat_level': combat, 'next_level': next_level, 'base_levels': base_levels,
        'melee_levels': melee_levels, 'prayer_levels': prayer_levels, 'range_levels': range_levels,
        'magic_levels': magic_levels, 'hitpoints_total': hitpoints+base_levels, 'defence_total': defence+base_levels,
        'attack_total': attack+melee_levels, 'strength_total': strength+melee_levels, 'magic_total': magic+magic_levels,
        'range_total': ranged+range_levels, 'prayer_total': prayer+prayer_levels
    };

    var $next_level_wrapper = $('#next_level_wrapper');
    var $next_level_template = $('#next_level_template');
    $next_level_wrapper.empty();
    $next_level_wrapper.append(handlebars_helper(next_level_data, $next_level_template));
}

function fill_combat_highscores(username, $highscore_username) {
    $highscore_username.val(username);

    $.when(highscore_lookup(username, 'hiscore_oldschool')).done(function(response) {
        var $highscore_inputs = $('.combat_input');

        for (var i = 0; i < $highscore_inputs.length; i++) {
            var $current_input = $($highscore_inputs[i]);
            $current_input.val(response[$current_input.attr('data-input_type')]['level'])
        }

        calculate_combat(response['Hitpoints']['level'], response['Attack']['level'], response['Strength']['level'],
        response['Defence']['level'], response['Magic']['level'], response['Ranged']['level'], response['Prayer']['level']);

        if(!$.isEmptyObject(response)){
            localStorage.setItem("username", username);
        }
    });
}

function fill_highscore_level(username, $highscore_username) {
    $highscore_username.val(username);
    var calc_type = $highscore_username.attr('data-type');
    var $current_level_input = $('#current_level_input');
    var $target_level_input = $current_level_input.siblings('#target_level_input');
    var $current_exp_input = $('#current_exp_input');

    $.when(highscore_lookup(username, 'hiscore_oldschool')).done(function(response) {
        var skill_data = response[calc_type];
        var current_skill_level = skill_data['level'];
        var current_exp = skill_data['exp'];
        var target_level = current_skill_level + 1;
        var target_exp = levels[target_level];

        $current_level_input.val(current_skill_level);
        $target_level_input.val(target_level);
        $current_exp_input.val(current_exp);

        var $amount = $('.amount');

        for (var i = 0; i < $amount.length; i++) {
            var $current_amount = $($amount[i]);
            var exp = parseFloat($current_amount.siblings('.exp').text());
            $current_amount.text(Math.ceil((target_exp - current_exp)/exp));
        }
    });
}

$(document).ready(function() {
    init();

    $(document).on('click', '#combat_calculator', function () {
        var calculator_url = globals.base_url + '/calculator/combat-calculator';

        window.location.replace(calculator_url);
        window.location.href = calculator_url;
    });

    $(document).on('click', '#prayer_calculator', function () {
        var calculator_url = globals.base_url + '/calculator/prayer-calculator';

        window.location.replace(calculator_url);
        window.location.href = calculator_url;
    });

    $(document).on('click', '#combat_submit', function () {
        var $highscore_submit = $(this);
        var $highscore_username = $highscore_submit.siblings('#highscore_username');
        var username = replace_all($highscore_username.val(), ' ', '_');

        fill_combat_highscores(username, $highscore_username);
    });

    $(document).on('keydown', '#highscore_username', function (e) {
        if(e.keyCode == 13) {
            $('.highscore_submit').click();
        }
    });

    $(document).on('keyup', '.combat_input', function () {
        var $table_container = $('.table_container');
        var hitpoints = $table_container.find('#hitpoints_input').val();
        var attack = $table_container.find('#attack_input').val();
        var strength = $table_container.find('#strength_input').val();
        var defence = $table_container.find('#defence_input').val();
        var magic = $table_container.find('#magic_input').val();
        var ranged = $table_container.find('#range_input').val();
        var prayer = $table_container.find('#prayer_input').val();

        calculate_combat(parseInt(hitpoints), parseInt(attack), parseInt(strength), parseInt(defence), parseInt(magic), parseInt(ranged), parseInt(prayer));
    });

    $(document).on('click', '#prayer_submit', function () {
        var $bones = $('.bone');
        var $ensouled = $('.ensouled');
        var gilded_altar = $('#gilded_input').is(':checked');
        var target_level = $('#target_level_input').val();
        var target_exp = levels[target_level];
        var current_exp = parseInt($('#current_exp_input').val());

        for (var i = 0; i < $bones.length; i++) {
            var $current_bone = $($bones[i]);
            var multiple = (gilded_altar) ? 3.5 : 4;
            var original_exp = parseFloat($current_bone.attr('data-exp'));
            var selling = parseInt($current_bone.attr('data-selling'));
            var exp = original_exp * multiple;
            var amount = Math.ceil((target_exp - current_exp)/exp);

            $current_bone.find('.exp').text(exp);
            $current_bone.find('.amount').text(number_comma_format(amount));
            $current_bone.find('.profit').text(number_comma_format(-(amount*selling)));
        }

        for (var h = 0; h < $ensouled.length; h++) {
            var $current_ensouled = $($ensouled[h]);
            var ensouled_exp = parseFloat($current_ensouled.attr('data-exp'));
            var ensouled_amount = Math.ceil((target_exp - current_exp)/ensouled_exp);
            var ensouled_selling = parseInt($current_ensouled.attr('data-selling'));

            $current_ensouled.find('.amount').text(number_comma_format(ensouled_amount));
            $current_ensouled.find('.profit').text(number_comma_format(-(ensouled_amount*ensouled_selling)));
        }
    });

    $('.sortable').click(function(){
        var table = $(this).parents('table').eq(0);
        var rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()));
        this.asc = !this.asc;
        if (!this.asc){rows = rows.reverse()}
        for (var i = 0; i < rows.length; i++){table.append(rows[i])}
    });
    function comparer(index) {
        return function(a, b) {
            var valA = parseFloat(getCellValue(a, index).replace(',', '')), valB = parseFloat(getCellValue(b, index).replace(',', ''));

            return valA - valB;
        }
    }
    function getCellValue(row, index){ return $(row).children('td').eq(index).html() }
});