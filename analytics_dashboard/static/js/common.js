/**
 * This defines our libraries across the application.  Each page
 * should load this file.
 */
var require = {
    baseUrl: '/static/',
    waitSeconds: 60,
    paths: {
        jquery: 'bower_components/jquery/dist/jquery.min',
        underscore: 'bower_components/underscore/underscore-min',
        backbone: 'bower_components/backbone/backbone',
        bootstrap: 'bower_components/bootstrap-sass-official/assets/javascripts/bootstrap',
        bootstrap_accessibility: 'bower_components/bootstrapaccessibilityplugin/plugins/js/bootstrap-accessibility.min',
        models: 'js/models',
        views: 'js/views',
        utils: 'js/utils',
        load: 'js/load',
        dataTables: 'bower_components/datatables/media/js/jquery.dataTables.min',
        dataTablesBootstrap: 'vendor/dataTables/dataTables.bootstrap',
        d3: 'bower_components/d3/d3.min',
        nvd3: 'bower_components/nvd3/nv.d3.min',
        topojson: 'bower_components/topojson/topojson',
        datamaps: 'bower_components/datamaps/dist/datamaps.world.min',
        moment: 'bower_components/moment/min/moment-with-locales.min',
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
        d3: {
            exports: 'd3'
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
