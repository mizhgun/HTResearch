//This function is called from index.js
function initiateTutorial() {
	/*var visited=getCookie("htresearch");
	if(visited)
		return;

   var expire=new Date();
   expire=new Date(expire.getTime()+7776000000);
   document.cookie="htresearch=here; expires="+expire;
	}*/

	$('#welcome-1').easyModal({
		closeButtonClass: '.welcome-close',
		autoOpen: true,
		onClose: initWelcome2
	});
}

function getCookie(name) {
	var arg=name+"=";
	var argLength=arg.length;
	var cookieLength=document.cookie.length;
	var i=0;
	while (i<cookieLength) {
	  var j=i+argLength;
	  if (document.cookie.substring(i,j) == arg)
	    return "here";
	  i=document.cookie.indexOf(" ",i)+1;
	  if (i==0) break;
	}
	return null;
}

function initWelcome2() {
	$('#welcome-2').easyModal({
		closeButtonClass: '.welcome-close',
		onClose: initWelcome3,
		overlayOpacity: 0.2,
		top: 50
	});

	$('#welcome-2').trigger('openModal');
}

function initWelcome3() {
	$('#welcome-3').easyModal({
		closeButtonClass: '.welcome-close',
		overlayOpacity: 0.2,
		top: window.innerHeight - 150
	});

	//The modal coordinates aren't properly constructed the first time for some reason
	//So the modal must be opened, closed, then opened again
	$('#welcome-3').trigger('openModal');
	$('#welcome-3').trigger('closeModal');
	$('#welcome-3').trigger('openModal');
}

function initWelcome4() {

}