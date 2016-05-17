/**
 * A layout view to manage app page rendering.
 */
define(function (require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        AlertView = require('learners/common/views/alert-view'),
        HeaderView = require('learners/app/views/header'),
        rootTemplate = require('text!learners/app/templates/root.underscore'),

        LearnersRootView;

    LearnersRootView = Marionette.LayoutView.extend({
        template: _.template(rootTemplate),

        regions: {
            alert: '.learners-alert-region',
            header: '.learners-header-region',
            main: '.learners-main-region'
        },

        childEvents: {
            appError: 'onAppError',
            appWarning: 'onAppWarning',
            clearError: 'onClearError',
            setFocusToTop: 'onSetFocusToTop'
        },

        initialize: function (options) {
            this.options = options || {};
        },

        onRender: function () {
            this.showChildView('header', new HeaderView({
                model: this.options.pageModel
            }));
        },

        onAppError: function (childView, options) {
            this.showAlert('error', options.title, options.description);
        },

        onAppWarning: function (childView, options) {
            this.showAlert('info', options.title, options.description);
        },

        onClearError: function () {
            this.hideAlert();
        },

        onSetFocusToTop: function () {
            this.$('#learner-app-focusable').focus();
        },

        /**
         * Renders an alert view.
         *
         * @param {string} type - the type of alert that should be shown.  Alert
         * types are defined in the AlertView module.
         * @param {string} title - the title of the alert.
         * @param {string} description - the description of the alert.
         */
        showAlert: function (type, title, description) {
            this.showChildView('alert', new AlertView({
                alertType: type,
                title: title,
                body: description
            }));
        },

        /**
         * Hides the alert view, if active.
         */
        hideAlert: function () {
            this.getRegion('alert').empty();
        }
    });

    return LearnersRootView;
});
