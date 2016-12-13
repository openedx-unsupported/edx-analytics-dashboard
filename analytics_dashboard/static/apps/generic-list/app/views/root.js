/**
 * A layout view to manage app page rendering.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        AlertView = require('generic-list/common/views/alert-view'),
        HeaderView = require('generic-list/app/views/header'),
        rootTemplate = require('text!generic-list/app/templates/root.underscore'),

        RootView;

    RootView = Marionette.LayoutView.extend({
        template: _.template(rootTemplate),

        regions: {
            alert: '.alert-region',
            header: '.header-region',
            main: '.main-region',
            navigation: '.navigation-region'
        },

        childEvents: {
            appError: 'onAppError',
            appWarning: 'onAppWarning',
            clearError: 'onClearError',
            setFocusToTop: 'onSetFocusToTop'
        },

        initialize: function(options) {
            this.options = options || {};
        },

        onRender: function() {
            this.showChildView('header', new HeaderView({
                model: this.options.pageModel
            }));
        },

        onAppError: function(childView, options) {
            this.showAlert('error', options.title, options.description);
        },

        onAppWarning: function(childView, options) {
            this.showAlert('info', options.title, options.description);
        },

        onClearError: function() {
            this.hideAlert();
        },

        /**
         * Renders an alert view.
         *
         * @param {string} type - the type of alert that should be shown.  Alert
         * types are defined in the AlertView module.
         * @param {string} title - the title of the alert.
         * @param {string} description - the description of the alert.
         * @param {object} link - the link for the alert. Has key "url"
         * (the href) and key "text" (the display text for the link).
         */
        showAlert: function(type, title, description, link) {
            this.showChildView('alert', new AlertView({
                alertType: type,
                title: title,
                body: description,
                link: link
            }));
        },

        /**
         * Hides the alert view, if active.
         */
        hideAlert: function() {
            this.getRegion('alert').empty();
        }
    });

    return RootView;
});
