/**
 * A layout view to manage app page rendering.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),

        RootView = require('generic-list/app/views/root'),
        rootTemplate = require('text!learners/app/templates/root.underscore'),

        LearnersRootView;

    LearnersRootView = RootView.extend({
        template: _.template(rootTemplate),

        regions: {
            alert: '.learners-alert-region',
            header: '.learners-header-region',
            main: '.learners-main-region',
            navigation: '.learners-navigation-region'
        }
    });

    return LearnersRootView;
});
