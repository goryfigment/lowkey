function init() {
    $('#grand_exchange_link').addClass('active');

    google.charts.load('current', {packages: ['corechart', 'line']});

    var d1 = new Date();
    d1.setUTCHours(0, 0, 0);
    d1.setUTCMilliseconds(0);

    var d2 = new Date();
    d2.setUTCHours(0, 0, 0);
    d2.setUTCMilliseconds(0);

    var d3 = new Date();
    d3.setUTCHours(0, 0, 0);
    d3.setUTCMilliseconds(0);

    globals.one_month_ago = d1.setUTCMonth(d1.getUTCMonth() - 1);
    globals.one_week_ago = d2.setUTCDate(d2.getUTCDate() - 7);
    globals.today = d3.valueOf();

    if(!$.isEmptyObject(globals.item_data)) {
        get_item_data(globals.item_data);
    } else if(!$.isEmptyObject(globals.high_alch)) {
        var $high_alch_template = $('#high_alch_template');
        var $high_alch_table_wrapper = $('#high_alch_table_wrapper');
        $high_alch_table_wrapper.append(handlebars_helper(globals.high_alch, $high_alch_template));
    } else if(!$.isEmptyObject(globals.result_list)) {
        //console.log(JSON.stringify(globals.result_list));
        var $result_template = $('#' + globals.result_type + '_template');
        var $result_wrapper = $('#result_wrapper');
        $result_wrapper.append(handlebars_helper(globals.result_list, $result_template));
    }
}

function epoch_to_utc(epoch_time) {
    var date = new Date(epoch_time);

    return new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(),  date.getUTCHours(),
        date.getUTCMinutes(), date.getUTCSeconds());
}

function number_type(number) {
    if(number > 0) {
        return 'positive';
    } else if(number < 0) {
        return 'negative'
    } else {
        return 'neutral'
    }
}

function get_item_data(item_data) {
    $.when(item_price(item_data['id'])).done(function(response) {
        //console.log(JSON.stringify(response));
        var $osrs_item_wrapper = $('#osrs_item_wrapper');
        var $item_template = $('#item_template');
        response['item_data'] = item_data;
        var $generated_html = handlebars_helper(response, $item_template);

        $osrs_item_wrapper.empty();
        $osrs_item_wrapper.append($generated_html);

        get_price_graph(item_data['id'], globals.one_month_ago)
    });
}

function get_price_data(item_id) {
    return $.ajax ({
        url: globals.base_url + '/item_price_data',
        data: {item_id: item_id},
        dataType: 'json',
        type: "GET"
    });
}

function item_price(item_id) {
    return $.ajax ({
        url: globals.base_url + '/grand-exchange/item_price',
        data: {item_id: item_id},
        dataType: 'json',
        type: "GET"
    });
}

function get_price_graph(item_id, start_time) {
    var post_data = {
        start_time: parseInt(start_time),
        item_id: parseInt(item_id)
    };

    $.ajax({
        url: globals.base_url + '/item_price_graph',
        data: post_data,
        dataType: 'json',
        type: "GET",
        success: function (response) {
            if (response['success']) {
                console.log(JSON.stringify(response));
                //console.log('https://api.rsbuddy.com/grandExchange?a=graph&g=1440&i=' + item_id + '&start=' + start_time)
                globals.item_price_graph = response;
                prepare_graph_data(response);
            } else {
                console.log(JSON.stringify(response));
            }
        }
    });
}

function prepare_graph_data(response, max_time, type) {
    var osbuddy_price_graph = response['osbuddy_price_graph'];
    var price_graph_array = [];
    var trade_graph_array = [];

    for (var i = 0; i < osbuddy_price_graph.length; i++) {
        var item = osbuddy_price_graph[i];

        if(max_time && parseInt(max_time) > parseInt(item['ts'])) {
            continue;
        }

        var item_date = epoch_to_utc(item['ts']);

        price_graph_array.push([item_date, response['osrs_price_graph'][item['ts']], item['buyingPrice'], item['sellingPrice']]);
        trade_graph_array.push([item_date, item['buyingCompleted'], item['sellingCompleted']]);
    }

    if(type && type == 'price') {
        google.charts.setOnLoadCallback(create_price_chart(price_graph_array));
    } else if(type && type == 'trade') {
        google.charts.setOnLoadCallback(create_trade_chart(trade_graph_array));
    } else {
        google.charts.setOnLoadCallback(load_charts(price_graph_array, trade_graph_array));
    }
}

function load_charts(price_array, trade_array) {
    create_price_chart(price_array);
    create_trade_chart(trade_array);
}

function create_price_chart(array) {
    var data = new google.visualization.DataTable();
    data.addColumn('date', 'Date');
    data.addColumn('number', 'GE Price');
    data.addColumn('number', 'Buying Price');
    data.addColumn('number', 'Selling Price');

    data.addRows(array);

    var options = {
        animation: {
            startup: true,
            duration: 1500,
            easing: 'out'
        },
        height: 450,
        width: 650,
        lineWidth: 3,
        pointSize: 4,
        chartArea: {
            left: '16%',
            right: '8%',
            top: '10%',
            bottom: '20%',
            width: '80%',
            height: '80%'
        },
        series: {
            0: { color: '#000000' },
            1: { color: '#0EC160' },
            2: { color: '#08E8FF' }
        },
        hAxis: {
            title: 'Date',
            format: 'MMM dd',
            gridlines: {
                color: 'transparent'
            }
        },
        vAxis: {
            title: 'Price (gp)',
            minValue: 0
        },
        legend: { position: 'none' },
        trendlines: {
            0: {
                type: 'polynomial',
                opacity: 0.4,
                pointSize: 0,
                tooltip: false,
                enableInteractivity: false
            }
        },
        focusTarget: 'category',
        backgroundColor: 'white'
    };

    $('#price_chart_wrapper').show();

    var chart = new google.visualization.LineChart(document.getElementById('price_chart_container'));

    chart.draw(data, options);
}

function create_trade_chart(array) {
    var data = new google.visualization.DataTable();
    data.addColumn('date', 'Date');
    data.addColumn('number', 'Buying Quantity');
    data.addColumn('number', 'Selling Quantity');

    data.addRows(array);

    var options = {
        animation: {
            startup: true,
            duration: 1500,
            easing: 'out'
        },
        height: 450,
        width: 650,
        lineWidth: 3,
        pointSize: 4,
        chartArea: {
            left: '16%',
            right: '8%',
            top: '10%',
            bottom: '20%',
            width: '80%',
            height: '80%'
        },
        series: {
            0: { color: '#0EC160' },
            1: { color: '#08E8FF' }
        },
        hAxis: {
            title: 'Date',
            format: 'MMM dd',
            gridlines: {
                color: 'transparent'
            }
        },
        vAxis: {
            title: 'Quantity',
            minValue: 0
        },
        legend: { position: 'none' },
        trendlines: {
            0: {
                type: 'polynomial',
                opacity: 0.4,
                pointSize: 0,
                tooltip: false,
                enableInteractivity: false
            }
        },
        focusTarget: 'category',
        backgroundColor: 'white'
    };

    $('#trade_chart_wrapper').show();

    var chart = new google.visualization.LineChart(document.getElementById('trade_chart_container'));

    chart.draw(data, options);
}

$(document).ready(function() {
    init();

    $(document).on('click', 'body', function () {
        var $ge_search_popup = $('#ge_search_popup');
        if($ge_search_popup.hasClass('active')){
            $ge_search_popup.removeClass('active');
        }
    });

    $(document).on('click', '#ge_search', function (e) {
        e.stopPropagation();

        var $ge_search_popup = $('#ge_search_popup');
        if(!$ge_search_popup.hasClass('active') && $ge_search_popup.children().length != 0){
            $ge_search_popup.addClass('active');
        }
    });

    $(document).on({
        mouseenter: function () {
            var $ge_item = $(this);
            var $active_ge_item = $ge_item.siblings('.selected');
            $active_ge_item.removeClass('selected');
            $ge_item.addClass('selected');
        },
        mouseleave: function () {
           $(this).removeClass("selected");
        }
    }, '.ge_item');

    var timer = null;
    $('#ge_search').keyup(function(e){
        clearTimeout(timer);
        timer = setTimeout(done_typing, 1000);

        function done_typing() {
            var $ge_search = $('#ge_search');
            var $ge_search_popup = $ge_search.siblings('#ge_search_popup');
            var $ge_items = $ge_search_popup.find('.ge_item');
            var $active_ge_item = $ge_search_popup.find('.ge_item.selected');
            var keycode = e.keyCode;

            if($ge_search_popup.is(':visible') && (keycode == 38 || keycode == 40)) {
                up_and_down_popups(keycode, $ge_search_popup, $ge_items, true);
                return;
            } else if(keycode == 13 && $active_ge_item.length) {
                $active_ge_item.click();
                return;
            }

            var search_value = $ge_search.val().toLowerCase().trim();

            var post_data = {
                search_value: search_value
            };

            if(search_value.length > 0) {
                $.ajax({
                    url: globals.base_url + '/grand-exchange/item_search',
                    data: post_data,
                    dataType: 'json',
                    type: "GET",
                    success: function (response) {
                        if (response['success']) {
                            //console.log(JSON.stringify(response));
                            var $ge_item_template = $('#ge_item_template');
                            var ge_list = response['item_list'];

                            $ge_search_popup.empty();

                            if(ge_list.length) {
                                $ge_search_popup.addClass('active');
                            } else {
                                $ge_search_popup.removeClass('active');
                            }

                            for (var i = 0; i < ge_list.length; i++) {
                                item_data = ge_list[i];

                                var $generated_html = handlebars_helper(item_data, $ge_item_template);
                                $generated_html.data('item_data', item_data);
                                $ge_search_popup.append($generated_html);
                            }
                        } else {
                            console.log(JSON.stringify(response));
                        }
                    }
                });
            }
        }
    });

    $(document).on('click', '.ge_item', function () {
        var $ge_item = $(this);
        var item_data = $ge_item.data('item_data');

        var $ge_search_popup = $ge_item.closest('#ge_search_popup');
        var $ge_search = $ge_search_popup.siblings('#ge_search');
        var $result_wrapper = $ge_search_popup.siblings('#result_wrapper');

        $ge_search_popup.removeClass('active');
        $ge_search.val(item_data['name']);
        $result_wrapper.empty();

        get_item_data(item_data);

        var url = globals.base_url + '/grand-exchange/' + parseInt(item_data['id']);
        window.history.pushState(item_data, item_data['name'], url);
    });

    $(document).on('click', '.graph_button', function () {
        var $graph_button = $(this);
        if($graph_button.hasClass('active')) {
            return;
        }

        $graph_button.siblings('.active').removeClass('active');
        $graph_button.addClass('active');

        var graph_type = $graph_button.attr('data-type');

        if($graph_button.is('#one_week_button')) {
            prepare_graph_data(globals.item_price_graph, globals.one_week_ago, graph_type);
        } else {
            prepare_graph_data(globals.item_price_graph, false, graph_type);
        }
    });

    $(document).on('click', '#smithing_button', function () {
        var $smithing_button = $(this);
        var $smithing_input = $smithing_button.siblings('#smithing_input');
        var smithing_level = $smithing_input.val();

        if(!$.isNumeric(smithing_level) || parseInt(smithing_level) < 0) {
            smithing_level = '0'
        } else if(parseInt(smithing_level) > 99) {
            smithing_level = '99'
        }

        var barrows_url = globals.base_url + '/grand-exchange/barrows-repair?smithing_level=' + smithing_level.toString();

        window.location.replace(barrows_url);
        window.location.href = barrows_url;
    });
});