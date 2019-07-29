
document.addEventListener('DOMContentLoaded', function() {

  //Tooltips
	var elems = document.querySelectorAll('.tooltipped');
  var instances = M.Tooltip.init(elems, {});

  //Modal
  var elems = document.querySelectorAll('.modal');
  var instances = M.Modal.init(elems, {
 		'onOpenEnd': initCarouselModal
  });

  //Date Picker
  var elems = document.querySelectorAll('.datepicker');
  var instances = M.Datepicker.init(elems, {
    'setDefaultDate': true, 
    'autoClose': true,
    'defaultDate': Date()
  });

  function initCarouselModal() {
    var elems = document.querySelectorAll('.carousel');
    var instances = M.Carousel.init(elems, {'fullWidth': true});
    instances[0].set(2);
  }
});