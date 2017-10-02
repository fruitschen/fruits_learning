$(document).ready(function(){
    // Initializes tooltips
    $('[title]').tooltip({container: 'body'});

    // Offset for Main Navigation
    $('#mainNav').affix({
        offset: {
            top: 100
        }
    })

});