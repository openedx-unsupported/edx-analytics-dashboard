/**
* This is where your tests go.  It should happen automatically when you
 * add files to the karma configuration.
*/

var isBrowser = window.__karma__ === undefined;
var specs = [];
var config = {
    // this is default location for the browser
    baseUrl: '/static/',
    paths: {
        jquery: 'vendor/jquery-1.11.1.min',
        bootstrap: 'vendor/bootstrap/javascripts/bootstrap',
        underscore: 'vendor/underscore-min',
        backbone: 'vendor/backbone-min',
        models: 'js/models',
        views: 'js/views',
        utils: 'js/utils',
        jasmine: 'vendor/jasmine/lib/jasmine-2.0.0/jasmine',
        'jasmine-html': 'vendor/jasmine/lib/jasmine-2.0.0/jasmine-html',
        boot: 'vendor/jasmine/lib/jasmine-2.0.0/boot',
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
        underscore: {
            exports: '_'
        },
        backbone: {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        },
        jasmine: {
            exports: 'jasmine'
        },
        'jasmine-html': {
            deps: ['jasmine'],
            exports: 'jasmine'
        },
        boot: {
            deps: ['jasmine', 'jasmine-html'],
            exports: 'window.jasmineRequire'
        },
        nvd3: {
            deps: ['d3'],
            exports: 'nv'
        },
        datamaps: {
            deps: ['topojson', 'd3'],
            exports: 'datamap'
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
};

// Two execution paths: browser or gulp
if(isBrowser) {
    // The browser cannot read directories, so all files must be enumerated below.
    specs = [
        config.baseUrl + 'js/spec/specs/attribute-view-spec.js',
        config.baseUrl + 'js/spec/specs/course-model-spec.js',
        config.baseUrl + 'js/spec/specs/tracking-model-spec.js',
        config.baseUrl + 'js/spec/specs/trends-view-spec.js',
        config.baseUrl + 'js/spec/specs/world-map-view-spec.js',
        config.baseUrl + 'js/spec/specs/tracking-view-spec.js',
        config.baseUrl + 'js/spec/specs/utils-spec.js',
        config.baseUrl + 'js/spec/specs/globalization-spec.js'
    ];
} else {
    // you can automatically get the test files using karma's configs
    for (var file in window.__karma__.files) {
        if (/spec\.js$/.test(file)) {
            specs.push(file);
        }
    }
    // This is where karma puts the files
    config.baseUrl = '/base/analytics_dashboard/static/';

    // Karma lets you list the test files here
    config.deps = specs;
    config.callback = window.__karma__.start;
}

require.config(config);

// the browser needs to kick off jasmine.  The gulp task does it through
// node
if(isBrowser) {
    //jasmine 2.0 needs boot.js to run, which loads on a window load, so this is
    // a hack
    // http://stackoverflow.com/questions/19240302/does-jasmine-2-0-really-not-work-with-require-js
    require(['boot'], function () {
        'use strict';
        require(specs,
            function () {
                window.onload();
            });
    });
}
