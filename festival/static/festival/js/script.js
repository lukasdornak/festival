var page = 0;
var readyToScroll = true;
var hashChanged = false;

function nextCheck(){
    if(hashChanged){
        hashCheck();
    }
}

function hashCheck(){
    hashChanged = false;
    var newPage = $pages.index($( window.location.hash.replace('#','#id-') ));
    if(newPage === -1){
        window.location.hash = $pages.eq(0).attr('id').replace('id-', '');
        return 0;
    }
    if( newPage !== page ){
        if(readyToScroll){
            readyToScroll = false;
            page = newPage;
            scrollToPage();
        } else {
            hashChanged = true;
        }
    }
}

function getScrolledPage(){
    for(p=$pages.length-1, len=0; p>=len; p-- ){
        if( $(document).scrollTop() > ($pages.eq(p).offset().top - 5) ){
            return p;
        }
    }
}

function scrollToPage(time=800){
    $('html, body').animate({
        scrollTop: $pages.eq(page).offset().top
    }, time);
    $('body').promise().done(function() {
        readyToScroll = true;
        nextCheck();
    });
}

function pageCheck(){
    var scrolled = getScrolledPage();
    if(page!=scrolled){
        page = scrolled;
        window.location.hash = $pages.eq(page).attr('id').replace('id-', '');
    }
}

$(function(){
    $pages = $('section');
    hashCheck();
    $(window).on('hashchange', function(event) {
        console.log('hashchango');
        hashCheck();
    });
    $(document).bind('scroll', function(event) {
        if(readyToScroll){
            pageCheck();
        } else {
            event.preventDefault();
        }
    });
    $('#menu_button').click(function() {
        $('#menu_button').toggleClass('cross');
        $('nav').toggleClass('hidden');
    });
    $('nav a').click(function() {
        $('nav').addClass('hidden');
        $('body').removeClass('first_time');
        $('#menu_button').removeClass('cross');
    });

    $('#lang_switch').mousedown(function () {
        $lang_switch = $('#lang_switch');
        var query_string = '';
        if ($('body').hasClass('first_time')) {
            query_string = 'home=1&';
        }
        if (!$('nav').hasClass('hidden')) {
            query_string = query_string + 'nav=1';
        }
        if (query_string) {
            $lang_switch.attr('href', $lang_switch.attr('href') + '?' + query_string);
        }
    });
    $('.nav-head').click(function () {
        $('.nav-list').addClass('hidden');
        $('#' + $(this).attr('id').replace('-head', '-list')).removeClass('hidden');
    })
});
