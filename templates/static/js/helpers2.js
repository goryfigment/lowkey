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



function handlebars_helper(response, $template, $container, empty_container, store_data) {
    var html_template = Handlebars.compile($template.html());
    var generated_html = html_template(response);

    if(empty_container) {
        $container.empty();
    }

    if(store_data) {
        generated_html.data('response', response);
    }

    $container.append(generated_html);
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

function handle_active_popup_keydown($popup, e) {
    if((e.keyCode == 38 || e.keyCode == 40) && $popup.is(':visible')) {
        e.preventDefault();
    } else if((e.keyCode == 38 || e.keyCode == 40) && !$popup.is(':visible')) {
        $popup.addClass('active');
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

function get_file_type_picture(file_name_or_type, file_json){
    var file_type = file_name_or_type;
    var file_type_picture_url = '/assets/file_icons/file_type_folder.png';

    if(file_type.indexOf('docx') > -1){
        file_type_picture_url = '/assets/file_icons/file_type_doc.png'
    }else if(file_type.indexOf('ppt') > -1){
        file_type_picture_url = '/assets/file_icons/file_type_ppt.png'
    }else if(file_type.indexOf('pdf') > -1){
        file_type_picture_url = '/assets/file_icons/file_type_pdf.png';
    }else if(file_type.indexOf('xls') > -1){
        file_type_picture_url = '/assets/file_icons/file_type_xls.png';
    }else if(file_type.indexOf('zip') > -1){
        file_type_picture_url = '/assets/file_icons/file_type_zip.png';
    }else if(file_type.indexOf('jpg') > -1 || file_type.indexOf('png') > -1 || file_type.indexOf('gif') > -1){
        try{
            if (file_json['file_url'] == undefined && file_json.indexOf('boxcloud') > -1){
                file_type_picture_url = file_json;
            } else {
                file_type_picture_url = file_json['file_url'];
            }
        } catch(err) {

        }

    }
    return file_type_picture_url;
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function handle_chosen_option($option, $input, $popup) {
    $input.val($option.attr('data-value'));

    $input.keyup();
    $popup.removeClass('active');

    var $selected = $popup.find('.selected');
    $selected.removeClass('selected');
}

//Takes in id source of handlebars template
//and the json to feed into it
//returns jquery html object
//function create_handlebars_template
function create_handlebars_object(source_id, json_data){
    var source = $(source_id).html();

    var template = Handlebars.compile(source);
    var generated_html = template(json_data);

    return generated_html;
}

//Checks if string_1 is in string_2
function string_in(str_1, str_2){

    if(str_2.toLowerCase().indexOf(str_1.toLowerCase()) > -1){
        return true;
    }
    return false;
}

//Takes in a list of jquery sets ex $('.class_name') and merges them
function merge_jquery_sets(set_list){
    var new_list = [];
    for(var i = 0; i < set_list.length; i++){
        new_list = new_list.concat(set_list[i].toArray());
    }
    return new_list;
}

function random_string(){
    return Math.random().toString(36).substring(7);
}

function redirect(url){
    window.location.href = url;
}

function dumps(json_obj){
    return JSON.stringify(json_obj);
}


function a_href_links(text){
    var urls = extract_urls(text);

    for(var i = 0; i < urls.length; i++){
        var url = urls[i].toString();

        var a_href_url = '<a target="_blank" href="' + url + '">' + url + '</a>';

        text = text.replace(url, a_href_url);
    }
    return text
}


//Parsess through a chunck of text to find an url the end is delimitted by a space and the front by either https

function extract_urls( text ) {

    try{
        var source = (text || '').toString();
        var urlArray = [];
        var url;
        var matchArray;
        var regexToken = /(((ftp|https?):\/\/)[\-\w@:%_\+.~#?,&\/\/=]+)|((www:)?[_.\w-]+([\w][\w\-]+\.)+[a-zA-Z]{2,3})/g;
        while( (matchArray = regexToken.exec( source )) !== null ) {
            var token = matchArray[0];
            if(token.indexOf('http') == -1){
                urlArray.push("http://" + token);

            }else{
                urlArray.push(token);
            }

        }

        return urlArray;
    }catch(err){
        return null;
    }


}

function extract_url( text ) {

    try{
        var source = (text || '').toString();
        var urlArray = [];
        var url;
        var matchArray;
        var regexToken = /(((ftp|https?):\/\/)[\-\w@:%_\+.~#?,&\/\/=]+)|((www:)?[_.\w-]+([\w][\w\-]+\.)+[a-zA-Z]{2,3})/g;
        while( (matchArray = regexToken.exec( source )) !== null ) {
            var token = matchArray[0];
            urlArray.push( token );
        }

        if(urlArray[0]) {
            if(urlArray[0][0] != 'h') urlArray[0] = "http://" + urlArray[0];
            return urlArray[0];
        }
        return null;
    }catch(err){
        return null;
    }


}



function log_error(err){
    try{
        console.log('%c' + err.toString(),'background: #222; color: #FF3300');
    }catch(err){
        console.log(err);
    }
}

function is_list(obj){
    if(!obj){
        return false;
    }

    if(Array.isArray(obj)){
        return true;
    }else{
        return false;
    }
}


function is_string(obj){
    if(!obj){
        return false;
    }

    if(typeof obj === 'string' || obj instanceof String){
        return true;
    }else{
        return false;
    }
}

function is_dict(obj){

    if(!obj) return false;
    if(Array.isArray(obj)) return false;

    if(obj.constructor != Object) return false;


    return true;

}

//Recursively updates dict1 with values from new_data_dict
function update_json(dict1, new_data_dict){

    $.each(new_data_dict, function(key, value){
        try{
            if(is_dict(new_data_dict[key])){
                dict1[key] = update_json(dict1[key], new_data_dict[key])
            }else{
                dict1[key] = value;
            }

        }catch(err){
            log_error(err);
        }

    });

    return dict1;
}


function update_jquery_element_json($jquery_obj, new_data_dict){
    var element_json_string = $jquery_obj.attr('data-json');
    if(element_json_string){
        try{
            var element_json = JSON.parse(element_json_string);
            element_json = update_json(element_json, new_data_dict);

            $jquery_obj.attr('data-json', JSON.stringify(element_json));
            return true;
        }catch(err){
            log_error(err);
            return null;
        }
    }else{
        return null;
    }

}







function get_equation_tag(){
    return '$';
}

//returns false if no equation tags are found,
//returns equation inside of $$ $$ if found
function has_equation_in_tags(str){
    var equation_tag_open = get_equation_tag();
    var equation_tag_close = get_equation_tag();


    //log('has_equation_tags()');

    var open_tag_index = str.indexOf(equation_tag_open);
    if(open_tag_index == -1){
        console.log("string doesnt contain open tag");
        return false;
    }



    //log('open_tag_index');
    //log(open_tag_index);


    var after_open_tag_substring = str.substring(open_tag_index + equation_tag_open.length, str.length);
    //log("after open tag substring");
    //log(after_open_tag_substring);

    var before_open_tag_length = str.length - after_open_tag_substring.length - equation_tag_open.length;

    //log('BEFORE OPEN TAG LENGTH: ' + before_open_tag_length.toString());

    var close_tag_index = after_open_tag_substring.indexOf(equation_tag_close);
    if(close_tag_index == -1){
        //log('string doesnt contain close tag');
        return false;
    }


    //add back length b4 open tag to get close_tag_index index in the str variable
    close_tag_index += before_open_tag_length + equation_tag_open.length;

    var equation_substring = str.substring(open_tag_index + equation_tag_open.length, close_tag_index);


    return equation_substring;

}

// Returns a random integer between min (included) and max (excluded)
// Using Math.round() will give you a non-uniform distribution!
function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min)) + min;
}

/*
 * Finds all instances of this_char in x_list
 * -John, Asfand, Luisa, Ganapathy
 */
function find_all_index(x_list, this_char, stop_at_index){
    if(typeof stop_at_index === 'undefined'){
        stop_at_index = null;
    }

    var indices = [];
    for(var i=0; i<x_list.length;i++) {

        if(is_list(this_char)){
            for(var y = 0; y < this_char.length; y++){
                if(this_char[y] == x_list[i]){
                    indices.push(i);


                    if(stop_at_index){
                        if(indices.length == stop_at_index){
                            return indices;
                        }
                    }
                }
            }
        }else{
            if (x_list[i] === this_char) {
                indices.push(i);
            }
        }

        if(stop_at_index){
            if(indices.length == stop_at_index){
                return indices;
            }
        }
    }
    return indices;
}

function is_undefined(obj){
    if(typeof(obj) == "undefined"){
        return true;
    }else{
        return false;
    }
}

function handle_undefined_string(str){
    if(!str){
        str = "";
    }
    return str;
}

function valid_image_url(file_url){
    file_url = file_url.toLowerCase();
    if(file_url.indexOf('png') > -1 || file_url.indexOf('jpg') > -1 || file_url.indexOf('gif') > -1 || file_url.indexOf('jpeg') > -1){
        console.log("VALID IMAGE URL - " + file_url);
        return true;
    }else{
        console.log("INVALID IMAGE URL - " + file_url);
        return false;
    }
}

function valid_image_file_upload_input($file_upload_input){
    var file_type = $file_upload_input[0].files[0].type;
    var ValidImageTypes = ["image/gif", "image/jpeg", "image/png"];
    if ($.inArray(file_type, ValidImageTypes) < 0) {
        console.log("INVALID File Type - " + file_type);
        return false;
    } else {
        return true;
    }
}

function get_file_type(file_name) {
    var re = /(?:\.([^.]+))?$/;
    var file_type = re.exec(file_name)[1];
    if(file_type == null || file_type == undefined) {
        return '';
    } else {
        return file_type;
    }
}

//TODO: Temp fix for a crashed chat -John
//TODO: We either need to fix word count or remove it. I don't think it's necessary -John
function wordCount(val){

    return {
        charactersNoSpaces : val.replace(/\s+/g, '').length,
        characters         : val.length,
        words              : 0,//val.match(/\S+/g).length,
        lines              : val.split(/\r*\n/).length
    }
}

function browser_check() {
    if((navigator.userAgent.indexOf("Opera") || navigator.userAgent.indexOf('OPR')) != -1 ) {
        return 'Opera';
    } else if(navigator.userAgent.indexOf("Chrome") != -1 ) {
        return 'Chrome';
    } else if(navigator.userAgent.indexOf("Safari") != -1) {
        return 'Safari';
    } else if(navigator.userAgent.indexOf("Firefox") != -1 ) {
        return 'Firefox';
    } else if((navigator.userAgent.indexOf("MSIE") != -1 ) || (!!document.documentMode == true )) {
        return 'IE';
    } else {
        return 'unknown';
    }
}

function bytes_to_mb(bytes) {
    return bytes / 1000000;
}

function format_mb(mb){
    mb = mb.toString();
    var dot_index = mb.indexOf('.');
    return mb.substring(0, dot_index + 3) + 'mb';
}

function bytes_to_kb(bytes) {
    return bytes / 1000;
}

function format_kb(mb){
    mb = mb.toString();
    var dot_index = mb.indexOf('.');
    return mb.substring(0, dot_index + 3) + 'kb';
}

function get_index(obj, obj_list){
    for(var i = 0; i < obj_list.length; i++){
        if(obj_list[i] == obj){
            return i;
        }
    }
    return -1;
}

function remove_white_space(string) {
    return string.replace(/\s+/g, " ").trim();
}

function str(obj, function_name){
    try{
        return obj.toString();
    }catch(err){
        console.log('This error is from the function: ' + function_name);
        console.log(err);
        return '';
    }
}