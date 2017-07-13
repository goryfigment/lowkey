function init() {
    $('#home-link').addClass('active');
}


$(document).ready(function() {
    init();

    $(document).on('click', '.title', function () {
        var url = globals.base_url + $(this).attr('data-url');

        window.location.replace(url);
        window.location.href = url;
    });
});