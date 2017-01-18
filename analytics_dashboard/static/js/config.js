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
        backgrid: 'bower_components/backgrid/lib/backgrid',
        'backgrid-filter': 'bower_components/backgrid-filter/backgrid-filter.min',
        'backgrid-paginator': 'bower_components/backgrid-paginator/backgrid-paginator.min',
        'backgrid-moment-cell': 'bower_components/backgrid-moment-cell/backgrid-moment-cell.min',
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
        nvd3: 'bower_components/nvd3/build/nv.d3',
        topojson: 'bower_components/topojson/topojson',
        datamaps: 'bower_components/datamaps/dist/datamaps.world',
        moment: 'bower_components/moment/min/moment-with-locales.min',
        text: 'bower_components/requirejs-plugins/lib/text',
        json: 'bower_components/requirejs-plugins/src/json',
        cldr: 'bower_components/cldrjs/dist/cldr',
        'cldr-data': 'bower_components/cldr-data',
        globalize: 'bower_components/globalize/dist/globalize',
        globalization: 'js/utils/globalization',
        marionette: 'bower_components/marionette/lib/core/backbone.marionette.min',
        uitk: 'bower_components/edx-ui-toolkit/src/js',
        // URI and its dependencies
        URI: 'bower_components/uri.js/src/URI',
        IPv6: 'bower_components/uri.js/src/IPv6',
        punycode: 'bower_components/uri.js/src/punycode',
        SecondLevelDomains: 'bower_components/uri.js/src/SecondLevelDomains',
        learners: 'apps/learners',
        'course-list': 'apps/course-list',
        components: 'apps/components',
        'axe-core': 'bower_components/axe-core/axe.min',
        sinon: 'bower_components/sinon/lib/sinon',
        nprogress: 'bower_components/nprogress/nprogress'
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
