define(['jquery', 'jquery.tmpl', 'bootstrap'], function($) {
    'use strict';

    var Modal = function(data) {
        this._data = data;
    };

    Modal.prototype = {
        createModal: function(selector, template) {
            var modal = $(selector).modal({
                show: false
            });

            var html = $(template).tmpl(this._data);
            modal.html(html);
            modal.modal('show');
        }
    };

    return Modal;
});