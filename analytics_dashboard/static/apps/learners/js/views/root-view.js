/**
 * A layout view to manage app page rendering.
 */
define([
    'learners/js/views/alert-view',
    'marionette',
    'text!learners/templates/app-container.underscore',
    'underscore'
], function (AlertView, Marionette, appContainerTemplate, _) {
    'use strict';

    var LearnersRootView = Marionette.LayoutView.extend({
        template: _.template(appContainerTemplate),
        regions: {
            error: '.learners-error-region',
            main: '.learners-main-region'
        },
        childEvents: {
            appError: 'onAppError',
            clearError: 'onClearError'
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
