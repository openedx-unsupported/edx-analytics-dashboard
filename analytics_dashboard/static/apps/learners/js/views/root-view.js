/**
 * A layout view to manage app page rendering.
 */
define([
    'learners/js/views/alert-view',
    'learners/js/views/header',
    'marionette',
    'text!learners/templates/app-container.underscore',
    'underscore'
], function (
    AlertView,
    HeaderView,
    Marionette,
    appContainerTemplate,
    _
) {
    'use strict';

    var LearnersRootView = Marionette.LayoutView.extend({
        template: _.template(appContainerTemplate),
        regions: {
            error: '.learners-error-region',
            header: '.learners-header-region',
            main: '.learners-main-region'
        },
        childEvents: {
            appError: 'onAppError',
            clearError: 'onClearError'
        },
        initialize: function (options) {
            this.options = options || {};
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
        }
    });

    return LearnersRootView;
});
