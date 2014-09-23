/**
 * This defines our libraries across the application.  Each page
 * should load this file.
 */
var require = {
    baseUrl: '/static/',
    waitSeconds: 60,
    paths: {
        jquery: 'vendor/jquery-1.11.1.min',
        underscore: 'vendor/underscore-min',
        backbone: 'vendor/backbone-min',
        bootstrap: 'vendor/bootstrap/javascripts/bootstrap.min',
        bootstrap_accessibility: 'vendor/bootstrap-accessibility-plugin/js/bootstrap-accessibility.min',
        models: 'js/models',
        views: 'js/views',
        utils: 'js/utils',
        load: 'js/load',
        holder: 'vendor/holder',
        dataTables: 'vendor/dataTables/jquery.dataTables.min',
        dataTablesBootstrap: 'vendor/dataTables/dataTables.bootstrap',
        d3: 'vendor/d3/d3',
        nvd3: 'vendor/nvd3/nv.d3',
        topojson: 'vendor/topojson/topojson',
        datamaps: 'vendor/datamaps/datamaps.world.min',
        moment: 'vendor/moment/moment-with-locales',
        text: 'bower_components/requirejs-plugins/lib/text',
        json: 'bower_components/requirejs-plugins/src/json',
        cldr: 'bower_components/cldrjs/dist/cldr',
        'cldr-data': 'bower_components/cldr-data',
        globalize: 'bower_components/globalize/dist/globalize',
        globalization: 'js/utils/globalization'
    },
    shim: {
        bootstrap: {
            deps: ['jquery']
        },
        bootstrap_accessibility: {
            deps: ['bootstrap']
        },
        underscore: {
            exports: '_'
        },
        backbone: {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone',
            init: function (_, $) {
                'use strict';
                Backbone.$ = $;
                return Backbone;
            }
        },
        dataTablesBootstrap: {
            deps: ['jquery', 'dataTables']
        },
        nvd3: {
            deps: ['d3'],
            exports: 'nv'
        },
        datamaps: {
            deps: ['topojson', 'd3'],
            exports: 'datamap'
        },
        moment: {
            noGlobal: true
        },
        json: {
            deps: ['text']
        },
        globalize: {
            deps: ['jquery', 'cldr'],
            exports: 'Globalize'
        },
        globalization: {
            deps: ['globalize'],
            exports: 'Globalize'
        }
    },
    // load jquery automatically
    deps: ['jquery']
};
