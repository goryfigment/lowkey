function init() {
    $('#calculator_link').addClass('active');

    var $calculator_wrapper = $('#calculator_wrapper');
    var $calculator_template = $(globals.template);

    $calculator_wrapper.append(handlebars_helper({}, $calculator_template));

    if (localStorage.getItem("username") !== null) {
        fill_combat_highscores(localStorage.getItem("username"), $('#highscore_username'));
    }
}

regular_url = 'http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player=G_o_RY';
ironman_url = 'http://services.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws?player=G_o_RY';
ultimate_url = 'http://services.runescape.com/m=hiscore_oldschool_ultimate/index_lite.ws?player=G_o_RY';
hardcore_url = 'http://services.runescape.com/m=hiscore_oldschool_hardcore_ironman/index_lite.ws?player=G_o_RY';
deadman_url = 'http://services.runescape.com/m=hiscore_oldschool_deadman/index_lite.ws?player=G_o_RY';
seasonal_url = 'http://services.runescape.com/m=hiscore_oldschool_seasonal/index_lite.ws?player=G_o_RY';

function highscore_lookup(username, highscore_type) {
    return $.ajax ({
        url: globals.base_url + '/calculator/highscore',
        data: {'username': username, 'type': highscore_type},
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

$(document).ready(function() {
    init();

    $(document).on('click', '#combat_calculator', function () {
        var calculator_url = globals.base_url + '/calculator/combat-calculator';

        window.location.replace(calculator_url);
        window.location.href = calculator_url;
    });

    $(document).on('click', '#highscore_submit', function () {
        var $highscore_submit = $(this);
        var $highscore_username = $highscore_submit.siblings('#highscore_username');
        var username = replace_all($highscore_username.val(), ' ', '_');

        fill_combat_highscores(username, $highscore_username);
    });

    $(document).on('keydown', '#highscore_username', function (e) {
        if(e.keyCode == 13) {
            $('#highscore_submit').click();
        }
    });

    $(document).on('keyup', '.combat_input', function (e) {
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
});