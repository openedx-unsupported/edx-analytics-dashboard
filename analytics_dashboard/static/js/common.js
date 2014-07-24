/**
 * This defines our libraries across the application.  Each page
 * should load this file using require.
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
        highcharts: 'vendor/highcharts.min',
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
        },
        highcharts: {
            exports: 'Highcharts'
        }
    },
     // load jquery automatically
    deps: ['jquery']
});

