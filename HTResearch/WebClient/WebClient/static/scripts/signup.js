$(document).ready(function(){
	$('#signup-form').validate({
		rules: {
			first_name: {
				maxlength: 25,
				required: true
			},
			last_name: {
				maxlength: 25,
				required: true
			},
			email: {
				maxlength: 60,
				required: true
			},
			account_type: {
				range: [0, 1],
				required: true
			},
			affiliation: {
				range: [0, 1]
			},
			organization: {
				maxlength: 60
			},
			background: {
				maxlength: 120,
				required: true
			},
			password: {
				rangelength: [8, 80],
				required: true
			},
			confirm_password: {
				equalTo: "#id_password"
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
			if($(element).closest('div').hasClass('radio')) {
				error.insertAfter($(element).closest('[id^="id_"]'));
			}
			else {
				error.insertAfter(element);
			}
		}
	});
});