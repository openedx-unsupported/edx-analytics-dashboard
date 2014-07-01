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
        bootstrap: 'vendor/bootstrap/javascripts/bootstrap.min',
        models: 'js/models',
        views: 'js/views',
        holder: 'vendor/holder'
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
            exports: 'Backbone',
            init: function (_, $) {
                'use strict';
                Backbone.$ = $; return Backbone; }
        }    },
     // load jquery and gettext automatically
    deps: ['jquery']
});

require(['jquery', 'underscore', 'backbone',
        'models/course-model', 'views/lens-navigation-view', 'bootstrap',
        'holder'],
    function ($, _, Backbone, CourseModel, LensNavigationView, bootstrap,
              holder) {
        'use strict';
        $(document).ready(function () {
            // ok, we've loaded all the libraries and the page is loaded, so
            // lets kick off our application
            var application = {

                onLoad: function() {
                    var model,
                        view,
                        jsonData = JSON.parse( $('#content')
                            .attr('data-analytics-init') );

                    // TODO: remove when we don't need the stub images anymore.
                    // holder is used to render visual placeholders
                    holder.run();

                    // this data will be set by something else eventually
                    model = new CourseModel();
                    // lets assume that django is passing us the data in the
                    // correct format for now
                    model.set(jsonData);

                    view = new LensNavigationView({model: model});
                    view.render();

                }

            };

            application.onLoad();
        });
    }
);

