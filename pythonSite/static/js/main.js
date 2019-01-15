

document.addEventListener('DOMContentLoaded', function() {
	M.AutoInit();



    var elems = document.querySelectorAll('.tooltipped');
    var instances = M.Tooltip.init(elems, options);

    // var elems = document.querySelectorAll('.modal');
    // var instances = M.Modal.init(elems, options);

    // var elems = document.querySelectorAll('.carousel');
    // var instances = M.Carousel.init(elems, options);

    var elems = document.querySelectorAll('.modal');
    var instances = M.Modal.init(elems, {
        'onOpenEnd': initCarouselModal
    });

    function initCarouselModal() {
        var elems = document.querySelectorAll('.carousel');
        var instances = M.Carousel.init(elems, {'fullWidth': true});
        instances[0].set(2);
    }
    
  }); 
