$(document).ready(function() {
    $(document).on('click', '#home_link, #logo_container', function () {
        window.location.href = 'http://' + window.location.host;
    });

    $(document).on('click', '#treasure_trail_link', function () {
        window.location.href = 'http://' + window.location.host + '/treasure_trails';
    });
});