/**
 * A layout view to manage app page rendering.
 *
 * Options:
 *  - pageModel: PageModel object
 *  - appClass: CSS class to prepend in root template HTML
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        AlertView = require('components/alert/views/alert-view'),
        HeaderView = require('components/header/views/header'),
        rootTemplate = require('components/root/templates/root.underscore'),

        RootView;

    RootView = Marionette.LayoutView.extend({
        template: _.template(rootTemplate),

        templateHelpers: function() {
            return this.options;
        },

        regions: function(options) {
            return {
                alert: _.template('.<%= appClass %>-alert-region')(options),
                header: _.template('.<%= appClass %>-header-region')(options),
                main: _.template('.<%= appClass %>-main-region')(options),
                navigation: _.template('.<%= appClass %>-navigation-region')(options)
            };
        },

        childEvents: {
            appError: 'onAppError',
            appWarning: 'onAppWarning',
            clearError: 'onClearError',
            setFocusToTop: 'onSetFocusToTop'
        },

        initialize: function(options) {
            this.options = _.defaults({displayHeader: true}, options);
        },

        onRender: function() {
            if (this.options.displayHeader) {
                this.showChildView('header', new HeaderView({
                    model: this.options.pageModel
                }));
            }
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
