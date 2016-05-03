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
            error: '.learners-error-region',
            header: '.learners-header-region',
            main: '.learners-main-region'
        },

        childEvents: {
            appError: 'onAppError',
            clearError: 'onClearError',
            setFocusToTop: 'onSetFocusToTop'
        },

        initialize: function (options) {
            this.options = options || {};

            // clear error message whenever the main section changes (e.g. detail
            // or roster pages shown)
            this.getRegion('main').on('before:show', this.onClearError.bind(this));
        },

        onRender: function () {
            this.showChildView('header', new HeaderView({
                model: this.options.pageModel
            }));
        },

        onAppError: function (childView, errorMessage) {
            this.showChildView('error', new AlertView({
                alertType: 'error',
                title: errorMessage
            }));
        },

        onClearError: function () {
            this.getRegion('error').empty();
        },

        onSetFocusToTop: function () {
            this.$('#learner-app-focusable').focus();
        }
    });

    return LearnersRootView;
});
