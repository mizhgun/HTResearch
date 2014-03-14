require(['shared/validators', 'jquery', 'bootstrap'], function(Validators, $) {
    'use strict';

    $(function (){
        $('input[type="url"]').blur(function() {
             Validators.checkURL(this);
        });

        $('#request-org-nav').addClass("active");
    });
});

