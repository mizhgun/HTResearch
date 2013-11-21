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
		closeButtonClass: '.welcome-close-1',
		autoOpen: true,
	});

	$('.welcome-close-1').click(initWelcome2);
	$('.welcome-close-2').click(initWelcome3);
	$('.welcome-close-3').click(initWelcome4);
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
		closeButtonClass: '.welcome-close-2',
		overlayOpacity: 0.2,
		top: 50
	});

	openEasyModal('#welcome-2');
}

function initWelcome3() {
	$('#welcome-3').easyModal({
		closeButtonClass: '.welcome-close-3',
		overlayOpacity: 0.2,
		top: window.innerHeight - 150,
	});

	openEasyModal('#welcome-3');
}

function initWelcome4() {
	$('#welcome-4').easyModal({
		closeButtonClass: '.welcome-close-4',
		overlayOpacity: 0.2,
		top: 100
	});

	openEasyModal('#welcome-4');
}

function openEasyModal(selector) {
	//The modal coordinates aren't properly constructed the first time for some reason
	//So the modal must be opened, closed, then opened again
	$(selector).trigger('openModal');
	$(selector).trigger('closeModal');
	$(selector).trigger('openModal');
	
}