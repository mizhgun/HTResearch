$(function() {
	$('#edit-contact-form').validate({
		rules: {
			first_name: {
				maxlength: 25
			},
			last_name: {
				maxlength: 25
			},
			email: {
				maxlength: 40
			},
			position: {
				maxlength: 60
			}
		},
		highlight: function (element) {
            $(element).closest('.form-group').addClass('has-error');
        },
        unhighlight: function (element) {
            $(element).closest('.form-group').removeClass('has-error');
        },
        errorElement: 'span',
        errorClass: 'help-block',
        errorPlacement: function (error, element) {
            if ($(element).closest('div').hasClass('radio')) {
                error.insertAfter($(element).closest('[id^="id_"]'));
            }
            else {
                error.insertAfter(element);
            }
        }
	});
});