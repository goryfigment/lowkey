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

Handlebars.registerHelper("math", function(firstValue, operator, secondValue, format) {
    firstValue = parseFloat(firstValue);
    secondValue = parseFloat(secondValue);

    var mathDict = {
        "+": firstValue + secondValue,
        "-": (firstValue - secondValue).toString().replace('-', '- '),
        "*": firstValue * secondValue,
        "/": firstValue / secondValue,
        "%": firstValue % secondValue
    };

    return (format) ? numberCommaFormat(mathDict[operator]) : mathDict[operator];
});

Handlebars.registerHelper("ceil", function(num, format) {
    return (format) ? numberCommaFormat(Math.ceil(num)) : Math.ceil(num);
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

Handlebars.registerHelper('replace', function(string, stringToReplace, stringReplacement) {
    return string.split(stringToReplace).join(stringReplacement);
});

Handlebars.registerHelper('asciiToChar', function(ascii) {
    return String.fromCharCode(ascii);
});

Handlebars.registerHelper('numCommaFormat', function(x) {
    return numberCommaFormat(x);
});

Handlebars.registerHelper('timePassed', function(x) {
    return timePassed(x);
});

Handlebars.registerHelper('accessDict', function(dict, key) {
    return dict[key.toString()];
});

Handlebars.registerHelper('isSubstring', function(substring, string) {
    if ((string.toString()).indexOf(substring) != -1) {
        return true;
    } else {
        return false;
    }
});

function timePassed(epochTime) {
    var d1 = new Date(parseInt(epochTime));
    var milliseconds = Math.abs(new Date() - d1);
    var minutes = Math.floor(milliseconds / 60000);
    var minuteString = '';
    var timestampString = '';

    if(minutes > 60) {
        var hours = Math.floor(minutes / 60);
        minutes = minutes - (hours * 60);
        var hourString = hours != 1 ? 'hours' : 'hour';
        minuteString = minutes != 1 ? 'minutes' : 'minute';
        timestampString = hours.toString() + ' ' + hourString + ' and ' + minutes.toString() + ' ' + minuteString;
    } else {
        minuteString = minutes != 1 ? 'minutes' : 'minute';
        timestampString = minutes.toString() + ' ' + minuteString;
    }

    return timestampString;
}

function numberCommaFormat(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function replaceAll(str, find, replace) {
    return str.replace(new RegExp(find.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1"), 'g'), replace);
}

function handlebarsHelper(response, $template) {
    var htmlTemplate = Handlebars.compile($template.html());
    var $generatedHtml = $(htmlTemplate(response));
    return $generatedHtml;
}

function scrollToElement($container, $element, speed){
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


function upAndDownPopups(keyCode, $popup, $options, scroll) {
    var $selected = $popup.find('.selected');
    var $firstOption = $options.filter(':visible').eq(0);
    var $lastOption = $options.filter(':visible').eq(-1);

    if (keyCode == 40) { //down arrow
        var $nextOption = $selected.nextAll($options).filter(':visible').first();
        if($selected.length) {
            $selected.removeClass('selected');
            if($nextOption.length){
                $nextOption.addClass('selected');
                if(scroll) {
                    scrollToElement($popup, $nextOption, 50);
                }
            } else{
                $firstOption.addClass('selected');
                if(scroll) {
                    scrollToElement($popup, $firstOption, 50);
                }
            }
        } else {
            $firstOption.addClass('selected');
            if(scroll) {
                scrollToElement($popup, $firstOption, 50);
            }
        }
    } else if (keyCode == 38) { //up arrow
        var $prevOption = $selected.prevAll($options).filter(':visible').first();
        if($selected.length) {
            $selected.removeClass('selected');
            if($prevOption.length){
                $prevOption.addClass('selected');
                if(scroll) {
                    scrollToElement($popup, $prevOption, 50);
                }
            }else{
                $lastOption.addClass('selected');
                if(scroll) {
                    scrollToElement($popup, $lastOption, 50);
                }
            }
        } else {
            $lastOption.addClass('selected');
            if(scroll) {
                scrollToElement($popup, $lastOption, 50);
            }
        }
    } else if(keyCode == 13) { //enter button
        $selected.trigger('click');
    }
}
