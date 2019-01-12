

document.addEventListener('DOMContentLoaded', function() {
	M.AutoInit();

    var elems = document.querySelectorAll('.tooltipped');
    var instances = M.Tooltip.init(elems, options);

    var elems = document.querySelectorAll('.modal');
    var instances = M.Modal.init(elems, options);
  }); 
