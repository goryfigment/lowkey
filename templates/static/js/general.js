$(document).ready(function() {
    $(document).on('click', '#grand_exchange', function () {
        var grand_exchange_url = globals.base_url + '/grand-exchange';

        window.location.replace(grand_exchange_url);
        window.location.href = grand_exchange_url;
    });

    $(document).on('click', '#treasure_trails', function () {
        var treasure_trails_url = globals.base_url + '/treasure-trails';

        window.location.replace(treasure_trails_url);
        window.location.href = treasure_trails_url;
    });

    $(document).on('click', '#calculator', function () {
        var calculator_url = globals.base_url + '/calculator';

        window.location.replace(calculator_url);
        window.location.href = calculator_url;
    });

    $(document).on('click', '#donate', function () {
        var donate_url = globals.base_url + '/donate';

        window.location.replace(donate_url);
        window.location.href = donate_url;
    });
});