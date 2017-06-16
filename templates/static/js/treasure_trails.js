function init() {
    $('#treasure_trail_link').addClass('active');
    $('#clue_search').focus();

    if(!$.isEmptyObject(globals.clue)) {
        var clue_data = globals.clue;
    } else {
        clue_data = localStorage.getItem("clue_data");
    }

    if(clue_data !== null && clue_data.length !== 0) {
        if(typeof clue_data == 'string') {
            clue_data = JSON.parse(clue_data);
        }

        if(!$.isEmptyObject(globals.clue) && globals.type != '') {
            var $clue_template = $('#clue_index_template');
            clue_data = {type: globals.type, clues: globals.clue}
        } else {
            $clue_template = $('#clue_template');
        }

        var $clue_result_container = $('#clue_result_container');
        var $generated_html = handlebars_helper(clue_data, $clue_template);

        $clue_result_container.empty();
        $clue_result_container.append($generated_html);
    }
}

function add_clue_data(clue_data) {
    if(globals.clue_data[clue_data['id']] !== undefined) {
        extra_clue_data = globals.clue_data[clue_data['id']];

        if(extra_clue_data['spot_title_1'] !== undefined && extra_clue_data['spot_title_2'] !== undefined) {
            clue_data['spot_title_1'] = extra_clue_data['spot_title_1'];
            clue_data['spot_title_2'] = extra_clue_data['spot_title_2'];
        }

        if(extra_clue_data['spot_title_3'] !== undefined) {
            clue_data['spot_title_3'] = extra_clue_data['spot_title_3'];
        }
    }

    return clue_data;
}

$(document).ready(function() {
    init();

    $(document).on('click', 'body', function () {
        var $clue_search_popup = $('#clue_search_popup');
        if($clue_search_popup.hasClass('active')){
            $clue_search_popup.removeClass('active');
        }
    });

    $(document).on('click', '#clue_search', function (e) {
        e.stopPropagation();

        var $clue_search_popup = $('#clue_search_popup');
        if(!$clue_search_popup.hasClass('active') && $clue_search_popup.children().length != 0){
            $clue_search_popup.addClass('active');
        }
    });

    $(document).on('click', '.clue_type', function (e) {
        var clue_type = $(this).attr('data-clue_type');

        $.ajax({
            url: globals.base_url + '/clue/type_search',
            data: {search_type: clue_type},
            dataType: 'json',
            type: "GET",
            success: function (response) {
                if (response['success']) {
                    console.log(JSON.stringify(response));
                } else {
                    console.log(JSON.stringify(response));
                }
            }
        });
    });

    $(document).on('keyup', '#clue_search', function (e) {
        var $clue_search = $(this);
        var $clue_search_popup = $clue_search.siblings('#clue_search_popup');
        var $clue_items = $clue_search_popup.find('.clue_item');
        var $active_clue_item = $clue_search_popup.find('.clue_item.selected');
        var keycode = e.keyCode;

        if($clue_search_popup.is(':visible') && (keycode == 38 || keycode == 40)) {
            up_and_down_popups(keycode, $clue_search_popup, $clue_items, true);
            return;
        } else if(keycode == 13 && $active_clue_item.length) {
            $active_clue_item.click();
            return;
        }

        var search_value = $clue_search.val().toLowerCase().trim();

        var post_data = {
            search_value: search_value
        };

        if(search_value.length > 0) {
            $.ajax({
                url: globals.base_url + '/clue/string_search',
                data: post_data,
                dataType: 'json',
                type: "GET",
                success: function (response) {
                    if (response['success']) {
                        //console.log(JSON.stringify(response));
                        var $clue_item_template = $('#clue_item_template');
                        var clue_list = response['clue_list'];

                        $clue_search_popup.empty();

                        if(clue_list.length) {
                            $clue_search_popup.addClass('active');
                        } else {
                            $clue_search_popup.removeClass('active');
                        }

                        for (var i = 0; i < clue_list.length; i++) {
                            clue_data = add_clue_data(clue_list[i]);

                            if(clue_data['type'] == 'coordinate') {
                                clue_data['clue'] = clue_data['clue'].replace('north', 'North')
                                    .replace('south', 'South').replace('east', 'East').replace('west', 'West');
                            }

                            if(clue_data['type'] == 'emote') {
                                clue_data['requirements'] = clue_data['requirements'].split(',');
                            }

                            var $generated_html = handlebars_helper(clue_data, $clue_item_template);
                            $generated_html.data('clue_data', clue_data);
                            $clue_search_popup.append($generated_html);
                        }
                    } else {
                        console.log(JSON.stringify(response));
                    }
                }
            });
        }
    });

    $(document).on('click', '.clue_item', function () {
        var $clue_item = $(this);
        var clue_data = $clue_item.data('clue_data');

        var $clue_search_popup = $clue_item.closest('#clue_search_popup');
        var $clue_search = $clue_search_popup.siblings('#clue_search');
        var $clue_result_container = $clue_search.siblings('#clue_result_container');
        var $clue_template = $('#clue_template');

        $clue_search_popup.removeClass('active');
        $clue_search.val(clue_data['clue']);

        var $generated_html = handlebars_helper(clue_data, $clue_template);
        $clue_result_container.empty();

        $clue_result_container.append($generated_html);
        localStorage.setItem("clue_data", JSON.stringify(clue_data));
        var url = globals.base_url + '/treasure-trails/' + parseInt(clue_data['id']);
        window.history.pushState(clue_data, clue_data['clue'], url);
    });

    $(document).on({
        mouseenter: function () {
            var $clue_item = $(this);
            var $active_clue_item = $clue_item.siblings('.selected');
            $active_clue_item.removeClass('selected');
            $clue_item.addClass('selected');
        },
        mouseleave: function () {
           $(this).removeClass("selected");
        }
    }, '.clue_item');

});