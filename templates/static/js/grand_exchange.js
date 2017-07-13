function init() {
    $('#grand-exchange-link').addClass('active');

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
        getItemData(globals.item_data);
    } else if(!$.isEmptyObject(globals.result_list)) {
        //console.log(JSON.stringify(globals.result_list));
        var $resultTemplate = $('#' + globals.result_type + '-template');
        var $resultWrapper = $('#result-wrapper');
        $resultWrapper.append(handlebarsHelper(globals.result_list, $resultTemplate));
    }
}

function epochToUtc(epochTime) {
    var date = new Date(epochTime);

    return new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(),  date.getUTCHours(),
        date.getUTCMinutes(), date.getUTCSeconds());
}

function getItemData(itemData) {
    $.when(itemPrice(itemData['id'])).done(function(response) {
        //console.log(JSON.stringify(response));
        var $osrsItemWrapper = $('#osrs-item-wrapper');
        var $itemTemplate = $('#item-template');
        response['item_data'] = itemData;
        var $generatedHtml = handlebarsHelper(response, $itemTemplate);

        $osrsItemWrapper.empty();
        $osrsItemWrapper.append($generatedHtml);

        getPriceGraph(itemData['id'], globals.one_month_ago)
    });
}

function itemPrice(itemId) {
    return $.ajax ({
        url: globals.base_url + '/grand-exchange/item_price',
        data: {item_id: itemId},
        dataType: 'json',
        type: "GET"
    });
}

function getPriceGraph(itemId, startTime) {
    var postData = {
        start_time: parseInt(startTime),
        item_id: parseInt(itemId)
    };

    $.ajax({
        url: globals.base_url + '/item_price_graph',
        data: postData,
        dataType: 'json',
        type: "GET",
        success: function (response) {
            if (response['success']) {
                //console.log(JSON.stringify(response));
                //console.log('https://api.rsbuddy.com/grandExchange?a=graph&g=1440&i=' + itemId + '&start=' + startTime)
                globals.item_price_graph = response;
                prepareGraphData(response);
            } else {
                console.log(JSON.stringify(response));
            }
        }
    });
}

function prepareGraphData(response, maxTime, type) {
    var osbuddyPriceGraph = response['osbuddy_price_graph'];
    var priceGraphArray = [];
    var tradeGraphArray = [];

    for (var i = 0; i < osbuddyPriceGraph.length; i++) {
        var item = osbuddyPriceGraph[i];

        if(maxTime && parseInt(maxTime) > parseInt(item['ts'])) {
            continue;
        }

        var itemDate = epochToUtc(item['ts']);

        priceGraphArray.push([itemDate, response['osrs_price_graph'][item['ts']], item['buyingPrice'], item['sellingPrice']]);
        tradeGraphArray.push([itemDate, item['buyingCompleted'], item['sellingCompleted']]);
    }

    if(type && type == 'price') {
        google.charts.setOnLoadCallback(createPriceChart(priceGraphArray));
    } else if(type && type == 'trade') {
        google.charts.setOnLoadCallback(createTradeChart(tradeGraphArray));
    } else {
        google.charts.setOnLoadCallback(loadCharts(priceGraphArray, tradeGraphArray));
    }
}

function loadCharts(priceArray, tradeArray) {
    createPriceChart(priceArray);
    createTradeChart(tradeArray);
}

function createPriceChart(array) {
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

    $('#price-chart-wrapper').show();

    var chart = new google.visualization.LineChart(document.getElementById('price-chart-container'));

    chart.draw(data, options);
}

function createTradeChart(array) {
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

    $('#trade-chart-wrapper').show();

    var chart = new google.visualization.LineChart(document.getElementById('trade-chart-container'));

    chart.draw(data, options);
}

$(document).ready(function() {
    init();

    $(document).on('click', 'body', function () {
        var $geSearchPopup = $('#ge-search-popup');
        if($geSearchPopup.hasClass('active')){
            $geSearchPopup.removeClass('active');
        }
    });

    $(document).on('click', '#ge-search', function (e) {
        e.stopPropagation();

        var $geSearchPopup = $('#ge-search-popup');
        if(!$geSearchPopup.hasClass('active') && $geSearchPopup.children().length != 0){
            $geSearchPopup.addClass('active');
        }
    });

    $(document).on({
        mouseenter: function () {
            var $geItem = $(this);
            var $activeGeItem = $geItem.siblings('.selected');
            $activeGeItem.removeClass('selected');
            $geItem.addClass('selected');
        },
        mouseleave: function () {
           $(this).removeClass("selected");
        }
    }, '.ge-item');

    var timer = null;
    $('#ge-search').keyup(function(e){
        clearTimeout(timer);
        timer = setTimeout(doneTyping, 1000);

        function doneTyping() {
            var $geSearch = $('#ge-search');
            var $geSearchPopup = $geSearch.siblings('#ge-search-popup');
            var $geItems = $geSearchPopup.find('.ge-item');
            var $activeGeItem = $geSearchPopup.find('.ge-item.selected');
            var keycode = e.keyCode;

            if($geSearchPopup.is(':visible') && (keycode == 38 || keycode == 40)) {
                upAndDownPopups(keycode, $geSearchPopup, $geItems, true);
                return;
            } else if(keycode == 13 && $activeGeItem.length) {
                $activeGeItem.click();
                return;
            }

            var searchValue = $geSearch.val().toLowerCase().trim();

            var postData = {
                search_value: searchValue
            };

            if(searchValue.length > 0) {
                $.ajax({
                    url: globals.base_url + '/grand-exchange/item_search',
                    data: postData,
                    dataType: 'json',
                    type: "GET",
                    success: function (response) {
                        if (response['success']) {
                            //console.log(JSON.stringify(response));
                            var $geItemTemplate = $('#ge-item-template');
                            var geList = response['item_list'];

                            $geSearchPopup.empty();

                            if(geList.length) {
                                $geSearchPopup.addClass('active');
                            } else {
                                $geSearchPopup.removeClass('active');
                            }

                            for (var i = 0; i < geList.length; i++) {
                                var itemData = geList[i];

                                var $generatedHtml = handlebarsHelper(itemData, $geItemTemplate);
                                $generatedHtml.data('item_data', itemData);
                                $geSearchPopup.append($generatedHtml);
                            }
                        } else {
                            console.log(JSON.stringify(response));
                        }
                    }
                });
            }
        }
    });

    $(document).on('click', '.ge-item', function () {
        var $geItem = $(this);
        var itemData = $geItem.data('item_data');

        var $geSearchPopup = $geItem.closest('#ge-search-popup');
        var $geSearch = $geSearchPopup.siblings('#ge-search');
        var $resultWrapper = $geSearchPopup.siblings('#result-wrapper');

        $geSearchPopup.removeClass('active');
        $geSearch.val(itemData['name']);
        $resultWrapper.empty();

        getItemData(itemData);

        var url = globals.base_url + '/grand-exchange/' + parseInt(itemData['id']);
        window.history.pushState(itemData, itemData['name'], url);
    });

    $(document).on('click', '.graph-button', function () {
        var $graphButton = $(this);
        if($graphButton.hasClass('active')) {
            return;
        }

        $graphButton.siblings('.active').removeClass('active');
        $graphButton.addClass('active');

        var graphType = $graphButton.attr('data-type');

        if($graphButton.is('#one-week-button')) {
            prepareGraphData(globals.item_price_graph, globals.one_week_ago, graphType);
        } else {
            prepareGraphData(globals.item_price_graph, false, graphType);
        }
    });

    $(document).on('click', '#smithing-button', function () {
        var $smithingButton = $(this);
        var $smithingInput = $smithingButton.siblings('#smithing-input');
        var smithingLevel = $smithingInput.val();

        if(!$.isNumeric(smithingLevel) || parseInt(smithingLevel) < 0) {
            smithingLevel = '0'
        } else if(parseInt(smithingLevel) > 99) {
            smithingLevel = '99'
        }

        var barrowsUrl = globals.base_url + '/grand-exchange/barrows-repair?smithing_level=' + smithingLevel.toString();

        window.location.replace(barrowsUrl);
        window.location.href = barrowsUrl;
    });
});