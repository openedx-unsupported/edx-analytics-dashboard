/**
 * Configuration for requires.js.
 */
require.config({
    baseUrl: '/static/',
    paths: {
        jquery: 'vendor/jquery-1.11.1.min',
        bootstrap: 'vendor/bootstrap/javascripts/bootstrap',
        underscore: 'vendor/underscore/underscore-min',
        backbone: 'vendor/backbone/backbone-min',
        models: 'js/models',
        views: 'js/views'
    },
    shim: {
        bootstrap: {
            deps: ['jquery']
        },
        underscore: {
            exports: '_'
        },
        backbone: {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        }
    }
});

require(['jquery', 'underscore', 'backbone', 'bootstrap',
        'models/course-model', 'views/lens-navigation-view'],
    function ($, _, Backbone, bootstrap, CourseModel, LensNavigationView) {
        'use strict';
        $(document).ready(function () {
            // ok, we've loaded all the libraries and the page is loaded, so
            // lets kick off our application
            var application = {

                onLoad: function() {
                    var model,
                        view;

                    // this data will be set by something else eventually
                    model = new CourseModel();
                    model.set({
                        courseId: edxAnalytics.initData.courseId
                    });

                    view = new LensNavigationView({model: model});
                    view.render();
                }

            };

            application.onLoad();
        });
    }
);

