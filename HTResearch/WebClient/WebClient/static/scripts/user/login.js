require(['jquery', 'jquery.validate', 'bootstrap'], function($) {
    $(function() {
        $('#login-nav').addClass('active');

        $('#login-form').validate({
            rules: {
                email: {
                    maxlength: 40,
                    required: true
                },
                password: {
                    rangelength: [8, 40],
                    required: true
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
                error.insertAfter(element);
            }
        });
    });
});
