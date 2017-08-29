function init() {
    $('#treasure-trail-link').addClass('active');
    $('#clue-search').focus();

    var clueData = null;

    if(!$.isEmptyObject(globals.clue)) {
        clueData = globals.clue;
    }

    if(clueData !== null && clueData.length !== 0) {
        var $clueResultContainer = $('#clue-result-container');
        $clueResultContainer.empty();

        if(typeof clueData == 'string') {
            clueData = JSON.parse(clueData);
        }

        if(!$.isEmptyObject(globals.clue) && globals.type != '') {
            var $clueTemplate = $('#clue-index-template');
            clueData = {type: globals.type, clues: globals.clue}
        } else {
            $clueTemplate = $('#clue-template');
        }

        var $generatedHtml = handlebarsHelper(clueData, $clueTemplate);
        $clueResultContainer.append($generatedHtml);
    }

    tippy('.tutorial', {annimation: 'shift', arrow: true});
}

function addClueData(clueData) {
    if(globals.clue_data[clueData['id']] !== undefined) {
        var extraClueData = globals.clue_data[clueData['id']];

        if(extraClueData['spot_title_1'] !== undefined && extraClueData['spot_title_2'] !== undefined) {
            clueData['spot_title_1'] = extraClueData['spot_title_1'];
            clueData['spot_title_2'] = extraClueData['spot_title_2'];
        }

        if(extraClueData['spot_title_3'] !== undefined) {
            clueData['spot_title_3'] = extraClueData['spot_title_3'];
        }
    }

    return clueData;
}

$(document).ready(function() {
    init();

    $(document).on('click', 'body', function () {
        var $clueSearchPopup = $('#clue-search-popup');
        if($clueSearchPopup.hasClass('active')){
            $clueSearchPopup.removeClass('active');
        }
    });

    $(document).on('click', '#clue-search', function (e) {
        e.stopPropagation();

        var $clueSearchPopup = $('#clue-search-popup');
        if(!$clueSearchPopup.hasClass('active') && $clueSearchPopup.children().length != 0){
            $clueSearchPopup.addClass('active');
        }
    });

    $(document).on('keyup', '#clue-search', function (e) {
        var $clueSearch = $(this);
        var $clueSearchPopup = $clueSearch.siblings('#clue-search-popup');
        var $clueItems = $clueSearchPopup.find('.clue-item');
        var $activeClueItem = $clueSearchPopup.find('.clue-item.selected');
        var keycode = e.keyCode;

        if($clueSearchPopup.is(':visible') && (keycode == 38 || keycode == 40)) {
            upAndDownPopups(keycode, $clueSearchPopup, $clueItems, true);
            return;
        } else if(keycode == 13 && $activeClueItem.length) {
            $activeClueItem.click();
            return;
        }

        var searchValue = $clueSearch.val().toLowerCase().trim();

        var postData = {
            search_value: searchValue
        };

        if(searchValue.length > 0) {
            $.ajax({
                url: globals.base_url + '/clue/string_search',
                data: postData,
                dataType: 'json',
                type: "GET",
                success: function (response) {
                    if (response['success']) {
                        //console.log(JSON.stringify(response));
                        var $clueItemTemplate = $('#clue-item-template');
                        var clueList = response['clue_list'];

                        $clueSearchPopup.empty();

                        if(clueList.length) {
                            $clueSearchPopup.addClass('active');
                        } else {
                            $clueSearchPopup.removeClass('active');
                        }

                        for (var i = 0; i < clueList.length; i++) {
                            var clueData = addClueData(clueList[i]);

                            if(clueData['type'] == 'coordinate') {
                                clueData['clue'] = clueData['clue'].replace('north', 'North')
                                    .replace('south', 'South').replace('east', 'East').replace('west', 'West');
                            }

                            if(clueData['type'] == 'emote') {
                                clueData['requirements'] = clueData['requirements'].split(',');
                                clueData['challenge'] = clueData['challenge'].split(',');
                                console.log(clueData)
                            }

                            var $generatedHtml = handlebarsHelper(clueData, $clueItemTemplate);
                            $generatedHtml.data('clue_data', clueData);
                            $clueSearchPopup.append($generatedHtml);
                        }
                    } else {
                        console.log(JSON.stringify(response));
                    }
                }
            });
        }
    });

    $(document).on('click', '.clue-item', function () {
        var $clueItem = $(this);
        var clueData = $clueItem.data('clue_data');

        var $clueSearchPopup = $clueItem.closest('#clue-search-popup');
        var $clueSearch = $clueSearchPopup.siblings('#clue-search');
        var $clueResultContainer = $clueSearch.siblings('#clue-result-container');
        var $clueTemplate = $('#clue-template');

        $clueSearchPopup.removeClass('active');
        $clueSearch.val(clueData['clue']);

        var $generatedHtml = handlebarsHelper(clueData, $clueTemplate);
        $clueResultContainer.empty();

        $clueResultContainer.append($generatedHtml);
        var url = globals.base_url + '/treasure-trails/' + parseInt(clueData['id']);
        window.history.pushState(clueData, clueData['clue'], url);
        tippy('.tutorial', {annimation: 'shift', arrow: true});
    });

    $(document).on({
        mouseenter: function () {
            var $clueItem = $(this);
            var $activeClueItem = $clueItem.siblings('.selected');
            $activeClueItem.removeClass('selected');
            $clueItem.addClass('selected');
        },
        mouseleave: function () {
           $(this).removeClass("selected");
        }
    }, '.clue-item');
});