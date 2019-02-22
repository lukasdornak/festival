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
        // if( $(document).scrollTop() > ($pages.eq(p).offset().top - head) ){
        if( $(document).scrollTop() > ($pages.eq(p).offset().top - 5) ){
            return p;
        }
    }
}

function scrollToPage(){
    $('html, body').animate({
        // scrollTop: $pages.eq(page).offset().top - head + 5
        scrollTop: $pages.eq(page).offset().top
    }, 800);
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
    // head = 70;
    hashCheck();
    $(window).on('hashchange', function(event) {
        hashCheck();
    });
    $(document).bind('scroll', function(event) {
        if(readyToScroll){
            pageCheck();
        } else {
            event.preventDefault();
        }
    });
    $('#menu_button').click(function(event) {
        $('nav').toggleClass('hidden');
    });
    $('nav a').click(function(event) {
        $('nav').addClass('hidden');
    });
})
