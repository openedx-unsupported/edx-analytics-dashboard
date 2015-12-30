/**
 * This defines our libraries across the application.  Each page
 * should load this file.
 */

require.config({
    baseUrl: '/static/',
    waitSeconds: 60,
    paths: {
        jquery: 'bower_components/jquery/dist/jquery',
        underscore: 'bower_components/underscore/underscore',
        backbone: 'bower_components/backbone/backbone',
        'backbone.paginator': 'bower_components/backbone.paginator/lib/backbone.paginator.min',
        'backbone.wreqr': 'bower_components/backbone.wreqr/lib/backbone.wreqr.min',
        'backbone.babysitter': 'bower_components/backbone.babysitter/lib/backbone.babysitter.min',
        bootstrap: 'bower_components/bootstrap-sass-official/assets/javascripts/bootstrap',
        bootstrap_accessibility: 'bower_components/bootstrapaccessibilityplugin/plugins/js/bootstrap-accessibility',
        models: 'js/models',
        collections: 'js/collections',
        views: 'js/views',
        utils: 'js/utils',
        load: 'js/load',
        datatables: 'bower_components/datatables/media/js/jquery.dataTables',
        dataTablesBootstrap: 'vendor/dataTables/dataTables.bootstrap',
        naturalSort: 'bower_components/natural-sort/naturalSort',
        d3: 'bower_components/d3/d3',
        nvd3: 'bower_components/nvd3/nv.d3',
        topojson: 'bower_components/topojson/topojson',
        datamaps: 'bower_components/datamaps/dist/datamaps.world',
        moment: 'bower_components/moment/min/moment-with-locales.min',
        text: 'bower_components/requirejs-plugins/lib/text',
        json: 'bower_components/requirejs-plugins/src/json',
        cldr: 'bower_components/cldrjs/dist/cldr',
        'cldr-data': 'bower_components/cldr-data',
        globalize: 'bower_components/globalize/dist/globalize',
        globalization: 'js/utils/globalization',
        collapsible: 'bower_components/edx-ui-toolkit/components/views/collapsible-view',
        marionette: 'bower_components/marionette/lib/core/backbone.marionette.min',
        components: 'bower_components/edx-ui-toolkit/components',
        // URI and its dependencies
        URI: 'bower_components/uri.js/src/URI',
        IPv6: 'bower_components/uri.js/src/IPv6',
        punycode: 'bower_components/uri.js/src/punycode',
        SecondLevelDomains: 'bower_components/uri.js/src/SecondLevelDomains'
    },
    wrapShim: true,
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
            deps: ['jquery', 'datatables']
        },
        naturalSort: {
            exports: 'naturalSort'
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
    }
});
