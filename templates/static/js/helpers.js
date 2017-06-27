Handlebars.registerHelper('ifCond', function (v1, operator, v2, options) {
    switch (operator) {
        case '==':
            return (v1 == v2) ? options.fn(this) : options.inverse(this);
        case '===':
            return (v1 === v2) ? options.fn(this) : options.inverse(this);
        case '<':
            return (v1 < v2) ? options.fn(this) : options.inverse(this);
        case '<=':
            return (v1 <= v2) ? options.fn(this) : options.inverse(this);
        case '>':
            return (v1 > v2) ? options.fn(this) : options.inverse(this);
        case '>=':
            return (v1 >= v2) ? options.fn(this) : options.inverse(this);
        case '&&':
            return (v1 && v2) ? options.fn(this) : options.inverse(this);
        case '||':
            return (v1 || v2) ? options.fn(this) : options.inverse(this);
        case '!=':
            return (v1 != v2) ? options.fn(this) : options.inverse(this);
        default:
            return options.inverse(this);
    }
});

Handlebars.registerHelper("math", function(first_value, operator, second_value, format) {
    first_value = parseFloat(first_value);
    second_value = parseFloat(second_value);

    var math_dict = {
        "+": first_value + second_value,
        "-": (first_value - second_value).toString().replace('-', '- '),
        "*": first_value * second_value,
        "/": first_value / second_value,
        "%": first_value % second_value
    };

    return (format) ? number_comma_format(math_dict[operator]) : math_dict[operator]
});

Handlebars.registerHelper('concat', function() {
    var outStr = '';
    for(var arg in arguments){
        if(typeof arguments[arg]!='object'){
            if(arguments[arg] == 'base_url') {
                arguments[arg] = globals.base_url;
            }
            outStr += arguments[arg];
        }
    }
    return outStr;
});

Handlebars.registerHelper('replace', function(string, string_to_replace, string_replacement) {
    return string.split(string_to_replace).join(string_replacement);
});

Handlebars.registerHelper('ascii_to_char', function(ascii) {
    return String.fromCharCode(ascii);
});

Handlebars.registerHelper('num_comma_format', function(x) {
    return number_comma_format(x);
});

Handlebars.registerHelper('time_passed', function(x) {
    return time_passed(x);
});

Handlebars.registerHelper('access_dict', function(dict, key) {
    return dict[key.toString()];
});

Handlebars.registerHelper('is_substring', function(substring, string) {
    if ((string.toString()).indexOf(substring) != -1) {
        return true;
    } else {
        return false;
    }
});

function time_passed(epoch_time) {
    var d1 = new Date(parseInt(epoch_time));
    var milliseconds = Math.abs(new Date() - d1);
    var minutes = Math.floor(milliseconds / 60000);
    var minute_string = '';

    if(minutes > 60) {
        var hours = Math.floor(minutes / 60);
        minutes = minutes - (hours * 60);
        var hour_string = hours != 1 ? 'hours' : 'hour';
        minute_string = minutes != 1 ? 'minutes' : 'minute';
        var timestamp_string = hours.toString() + ' ' + hour_string + ' and ' + minutes.toString() + ' ' + minute_string
    } else {
        minute_string = minutes != 1 ? 'minutes' : 'minute';
        timestamp_string = minutes.toString() + ' ' + minute_string
    }

    return timestamp_string;
}

function number_comma_format(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function replace_all(str, find, replace) {
    return str.replace(new RegExp(find.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1"), 'g'), replace);
}

function handlebars_helper(response, $template) {
    var html_template = Handlebars.compile($template.html());
    var $generated_html = $(html_template(response));
    return $generated_html;
}

function scroll_to_element($container, $element, speed){
    var elementTop = $element.offset().top;
    var elementHeight = $element.height();
    var containerTop = $container.offset().top;
    var containerHeight = $container.height();

    if ((((elementTop - containerTop) + elementHeight) > 0) && ((elementTop - containerTop) < containerHeight)) {

    } else {
        $container.animate({
            scrollTop: $element.offset().top - $container.offset().top + $container.scrollTop()
        }, speed);
    }
}


function up_and_down_popups(keyCode, $popup, $options, scroll) {
    var $selected = $popup.find('.selected');
    //var $visible_options = $popup
    var $first_option = $options.filter(':visible').eq(0);
    var $last_option = $options.filter(':visible').eq(-1);
    //alert($first_option.attr('data-value'));

    if (keyCode == 40) { //down arrow
        var $next_option = $selected.nextAll($options).filter(':visible').first();
        if($selected.length) {
            $selected.removeClass('selected');
            if($next_option.length){
                $next_option.addClass('selected');
                if(scroll) {
                    scroll_to_element($popup, $next_option, 50);
                }
            } else{
                $first_option.addClass('selected');
                if(scroll) {
                    scroll_to_element($popup, $first_option, 50);
                }
            }
        } else {
            $first_option.addClass('selected');
            if(scroll) {
                scroll_to_element($popup, $first_option, 50);
            }
        }
    } else if (keyCode == 38) { //up arrow
        var $prev_option = $selected.prevAll($options).filter(':visible').first();
        if($selected.length) {
            $selected.removeClass('selected');
            if($prev_option.length){
                $prev_option.addClass('selected');
                if(scroll) {
                    scroll_to_element($popup, $prev_option, 50);
                }
            }else{
                $last_option.addClass('selected');
                if(scroll) {
                    scroll_to_element($popup, $last_option, 50);
                }
            }
        } else {
            $last_option.addClass('selected');
            if(scroll) {
                scroll_to_element($popup, $last_option, 50);
            }
        }
    } else if(keyCode == 13) { //enter button
        $selected.trigger('click');
    }
}