require(['shared/validators', 'jquery', 'jquery.validate', 'bootstrap'], function(Validators, $) {
    $(function() {
        $('input[type="url"]').blur(function() {
             Validators.checkURL(this);
        });

        $('#edit-organization-form').validate({
            rules: {
                name: {
                    maxlength: 80
                },
                organization_url: {
                    url: true
                },
                facebook: {
                    url: true,
                    maxlength: 60
                },
                twitter: {
                    url: true,
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
});
