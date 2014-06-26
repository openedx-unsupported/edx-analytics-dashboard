/**
 * Configuration for requires.js.
 */
require.config({
    baseUrl: '/static/',
    waitSeconds: 60,
    paths: {
        jquery: 'vendor/jquery-1.11.1.min',
        underscore: 'vendor/underscore-min',
        backbone: 'vendor/backbone-min',
        bootstrap: 'vendor/bootstrap/javascripts/bootstrap',
        models: 'js/models',
        views: 'js/views'
    },
    shim: {
        bootstrap: {
            deps: ['jquery'],
            // http://stackoverflow.com/questions/13377373/shim-twitter-bootstrap-for-requirejs
            // for making sure that bootstrap is loaded correctly
            exports: '$.fn.popover'
        },
        underscore: {
            exports: '_'
        },
        backbone: {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone',
            init: function (_, $) { Backbone.$ = $; return Backbone; }
        },
        "jquery.cookie": {
                deps: ["jquery"],
                exports: "jQuery.fn.cookie"
        }
    },
     // load jquery and gettext automatically
    deps: ['jquery']
});

require(['jquery', 'underscore', 'backbone',
        'models/course-model', 'views/lens-navigation-view', 'bootstrap'],
    function ($, _, Backbone, CourseModel, LensNavigationView) {
        'use strict';
        $(document).ready(function () {
            // ok, we've loaded all the libraries and the page is loaded, so
            // lets kick off our application
            var application = {

                onLoad: function() {
                    var model,
                        view,
                        jsonData = JSON.parse( $('#analytics-init-data').attr('data') );

                    // this data will be set by something else eventually
                    model = new CourseModel();
                    // lets assume that django is passing us the data in the correct format for now
                    model.set(jsonData);

                    view = new LensNavigationView({model: model});
                    view.render();
                }

            };

            application.onLoad();
        });
    }
);

