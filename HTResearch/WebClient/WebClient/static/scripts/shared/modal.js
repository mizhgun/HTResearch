/**
 * Provides a means of creating Bootstrap modals.
 *
 * @module modal
 */
define(['jquery', 'jquery.tmpl', 'bootstrap'], function($) {
    'use strict';

    /**
     * Creates a new Bootstrap modal.
     * @param {object} data The data to be bound to the modal.
     * @param {string} selector The JQuery selector for the target DOM element.
     * @param {string} template The JQuery selector for the target template.
     */
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