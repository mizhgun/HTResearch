define(['shared/validators','jquery'], function(Validators, $) {
    $(function (){
        $('input[type="url"]').blur(function() {
             Validators.checkURL(this);
        });

        $('#request-org-nav').addClass("active");
    });
});

