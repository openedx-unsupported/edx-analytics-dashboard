/**
 * A layout view to manage app page rendering.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),

        RootView = require('generic-list/app/views/root')
        rootTemplate = require('text!course-list/app/templates/root.underscore'),

        CourseListRootView;

    CourseListRootView = RootView({
        template: _.template(rootTemplate),

        regions: {
            alert: '.course-list-alert-region',
            header: '.course-list-header-region',
            main: '.course-list-main-region',
            navigation: '.course-list-navigation-region'
        }
    });

    return CourseListRootView;
});
