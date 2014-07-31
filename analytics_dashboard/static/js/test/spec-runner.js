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
        highcharts: 'vendor/highcharts/highcharts.min'
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
        }
    }
};

// there are two paths -- one for running this in browser and one for running
// via gulp
if(isBrowser) {
    // unfortunately, we can't read directories in the browser, so we need to
    // list them here -- sorry!
    specs = [
        config.baseUrl + 'js/spec/specs/course-model-spec.js',
        config.baseUrl + 'js/spec/specs/tracking-model-spec.js',
        config.baseUrl + 'js/spec/specs/enrollment-trend-view-spec.js',
        config.baseUrl + 'js/spec/specs/tracking-view-spec.js',
        config.baseUrl + 'js/spec/specs/utils-spec.js'
    ];
} else {
    // you can automatically get the test files using karma's configs
    for (var file in window.__karma__.files) {
        if (/spec\.js$/.test(file)) {
            specs.push(file);
        }
    }
    // this is where karma puts the files
    config.baseUrl = '/base/analytics_dashboard/static/';
    // karam lets you list the test files here
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
