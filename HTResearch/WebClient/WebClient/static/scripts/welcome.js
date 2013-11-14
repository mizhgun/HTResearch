//This function is called from index.js
function initiateTutorial() {
	/*var visited=getCookie("htresearch");

	if (!visited){
	   var expire=new Date();
	   expire=new Date(expire.getTime()+7776000000);
	   document.cookie="htresearch=here; expires="+expire;
	}*/
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
