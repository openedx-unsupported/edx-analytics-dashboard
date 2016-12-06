/**
 * A layout view to manage app page rendering.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        AlertView = require('course-list/common/views/alert-view'),
        HeaderView = require('course-list/app/views/header'),
        rootTemplate = require('text!course-list/app/templates/root.underscore'),

        CourseListRootView;

    CourseListRootView = Marionette.LayoutView.extend({
        template: _.template(rootTemplate),

        regions: {
            alert: '.course-list-alert-region',
            header: '.course-list-header-region',
            main: '.course-list-main-region',
            navigation: '.course-list-navigation-region'
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

    return CourseListRootView;
});
