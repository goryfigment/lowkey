$(document).ready(function() {
    $(document).on('click', '#grand_exchange', function () {
        var grand_exchange_url = globals.base_url + '/grand_exchange';

        window.location.replace(grand_exchange_url);
        window.location.href = grand_exchange_url;
    });

    $(document).on('click', '#treasure_trails', function () {
        var treasure_trails_url = globals.base_url + '/treasure_trails';

        window.location.replace(treasure_trails_url);
        window.location.href = treasure_trails_url;
    });
});