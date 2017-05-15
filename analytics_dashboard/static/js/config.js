/**
 * This defines our libraries across the application.  Each page
 * should load this file.
 */

require.config({
    baseUrl: '/static/',
    waitSeconds: 60,
    paths: {
        jquery: 'node_modules/jquery/dist/jquery',
        underscore: 'node_modules/underscore/underscore',
        backbone: 'node_modules/backbone/backbone',
        'backbone.paginator': 'node_modules/backbone.paginator/lib/backbone.paginator.min',
        'backbone.wreqr': 'node_modules/backbone.wreqr/lib/backbone.wreqr.min',
        'backbone.babysitter': 'node_modules/backbone.babysitter/lib/backbone.babysitter.min',
        backgrid: 'node_modules/backgrid/lib/backgrid',
        'backgrid-filter': 'node_modules/backgrid-filter/backgrid-filter.min',
        'backgrid-paginator': 'node_modules/backgrid-paginator/backgrid-paginator.min',
        'backgrid-moment-cell': 'node_modules/backgrid-moment-cell/backgrid-moment-cell.min',
        bootstrap: 'node_modules/bootstrap-sass/assets/javascripts/bootstrap',
        bootstrap_accessibility: 'node_modules/bootstrap-accessibility-plugin/plugins/js/bootstrap-accessibility',
        models: 'js/models',
        collections: 'js/collections',
        views: 'js/views',
        utils: 'js/utils',
        load: 'js/load',
        datatables: 'node_modules/datatables/media/js/jquery.dataTables',
        dataTablesBootstrap: 'vendor/dataTables/dataTables.bootstrap',
        naturalSort: 'node_modules/js-natural-sort/dist/naturalsort',
        d3: 'node_modules/d3/d3',
        nvd3: 'node_modules/nvd3/build/nv.d3',
        topojson: 'node_modules/topojson/topojson',
        datamaps: 'node_modules/datamaps/dist/datamaps.world',
        moment: 'node_modules/moment/min/moment-with-locales.min',
        text: 'node_modules/requirejs-plugins/lib/text',
        json: 'node_modules/requirejs-plugins/src/json',
        cldr: 'node_modules/cldrjs/dist/cldr',
        'cldr-data': 'node_modules/cldr-data',
        globalize: 'node_modules/globalize/dist/globalize',
        globalization: 'js/utils/globalization',
        marionette: 'node_modules/backbone.marionette/lib/core/backbone.marionette.min',
        uitk: 'node_modules/edx-ui-toolkit/src/js',
        // URI and its dependencies
        URI: 'node_modules/urijs/src/URI',
        IPv6: 'node_modules/urijs/src/IPv6',
        punycode: 'node_modules/urijs/src/punycode',
        SecondLevelDomains: 'node_modules/urijs/src/SecondLevelDomains',
        learners: 'apps/learners',
        'course-list': 'apps/course-list',
        components: 'apps/components',
        'axe-core': 'node_modules/axe-core/axe.min',
        sinon: 'node_modules/sinon/lib/sinon',
        nprogress: 'node_modules/nprogress/nprogress'
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
            /* eslint-disable no-undef */
            init: function(_, $) {
                'use strict';
                Backbone.$ = $;
                return Backbone;
            }
            /* eslint-enable no-undef */
        },
        backgrid: {
            deps: ['backbone', 'underscore', 'jquery'],
            exports: 'Backgrid'
        },
        'backgrid-filter': {
            deps: ['backbone', 'underscore', 'backgrid']
        },
        'backgrid-paginator': {
            deps: ['backbone', 'underscore', 'jquery', 'backgrid']
        },
        'backgrid-moment-cell': {
            deps: ['backbone', 'underscore', 'moment', 'backgrid']
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
        },
        'axe-core': {
            exports: 'axe'
        }
    }
});
