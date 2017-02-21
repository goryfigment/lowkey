try{
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
}catch(err){
    console.log("Error registering handlebars helper in helpers2.js");
}

Handlebars.registerHelper('concat', function() {
    var outStr = '';
    for(var arg in arguments){
        if(typeof arguments[arg]!='object'){
            outStr += arguments[arg];
        }
    }
    return outStr;
});


function handlebars_helper(response, $template, $container, store_data) {
    var html_template = Handlebars.compile($template.html());
    var $generated_html = $(html_template(response));
    return $generated_html;

    //if(store_data) {
    //    $(generated_html).data('response', JSON.stringify(response));
    //    console.log($(generated_html).data('response'));
    //}
    //
    //$container.append(generated_html);
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