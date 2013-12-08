$(document).ready(function(){
	$('#login-form').validate({
		rules: {
			email: {
				maxlength: 60,
				required: true
			},
			password: {
				rangelength: [8, 80],
				required: true
			}
		},
		highlight: function(element) {
			$(element).closest('.form-group').addClass('has-error');
		},
		unhighlight: function(element) {
			$(element).closest('.form-group').removeClass('has-error');
		},
		errorElement: 'span',
		errorClass: 'help-block',
		errorPlacement: function(error, element) {
			error.insertAfter(element);
		}
	});
});