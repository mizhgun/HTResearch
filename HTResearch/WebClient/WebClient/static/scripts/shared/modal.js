define(['jquery', 'jquery.tmpl', 'bootstrap'], function($) {
    'use strict';

    function createModal(data, selector, template) {
        var modal = $(selector).modal({
            show: false
        });

        var html = $(template).tmpl(data);
        modal.html(html);
        modal.modal('show');
    }

    return { createModal: createModal };
});