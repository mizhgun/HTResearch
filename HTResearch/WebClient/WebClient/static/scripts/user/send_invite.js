require(['jquery', 'jquery.validate', 'bootstrap'], function($) {
    $(function() {
        $('#invite-nav').addClass('active');

        $('#invite-form').validate({
            rules: {
                email: {
                    maxlength: 40,
                    required: true
                },
                message: {
                    maxlength: 280,
                    required: false
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
