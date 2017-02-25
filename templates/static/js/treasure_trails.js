function init() {
    $('#treasure_trail_link').addClass('active');
    $('#clue_search').focus();

    var clue_data = localStorage.getItem("clue_data");

    if(clue_data.length) {
        clue_data = JSON.parse(clue_data);

        if(clue_data['keywords'] == '0000N0713W') {
            return;
        }

        var $coordinate_template = $('#coordinate_template');
        var $clue_result_container = $('#clue_result_container');
        var $generated_html = handlebars_helper(clue_data, $coordinate_template);

        $clue_result_container.empty();
        $clue_result_container.append($generated_html);
    }
}

$(document).ready(function() {

    init();

    //Search for a clue stored in database
    $(document).on('keyup', '#clue_search', function (e) {
        var $clue_search = $(this);

        var $clue_search_popup = $clue_search.siblings('#clue_search_popup');
        var $clue_items = $clue_search_popup.find('.clue_item');
        var $active_clue_item = $clue_search_popup.find('.clue_item.selected');

        //Handle up and down
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
                url: globals.base_url + '/clue/search',
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
                            if(clue_list[i]['type'] == 'coordinate') {
                                clue_list[i]['clue'] = clue_list[i]['clue'].replace('north', 'North')
                                    .replace('south', 'South').replace('east', 'East').replace('west', 'West');
                            }

                            var $generated_html = handlebars_helper(clue_list[i], $clue_item_template);
                            $generated_html.data('clue_data', clue_list[i]);
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
        console.log(clue_data);

        var $clue_search_popup = $clue_item.closest('#clue_search_popup');
        var $clue_search = $clue_search_popup.siblings('#clue_search');
        var $clue_result_container = $clue_search.siblings('#clue_result_container');
        var $coordinate_template = $('#coordinate_template');

        $clue_search_popup.removeClass('active');
        $clue_search.val(clue_data['clue']);

        var $generated_html = handlebars_helper(clue_data, $coordinate_template);
        $clue_result_container.empty();

        $clue_result_container.append($generated_html);
        localStorage.setItem("clue_data", JSON.stringify(clue_data));
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