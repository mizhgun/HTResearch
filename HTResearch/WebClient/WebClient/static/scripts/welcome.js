$('.btn').click(function(){
	var expire=new Date();
   	expire=new Date(expire.getTime()+7776000000);
   	document.cookie="htresearch=amaterasu; expires="+expire;

   	window.location = '/';
})