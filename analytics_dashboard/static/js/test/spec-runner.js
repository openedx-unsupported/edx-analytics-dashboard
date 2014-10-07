/**
* This is where your tests go.  It should happen automatically when you
 * add files to the karma configuration.
*/

var isBrowser = window.__karma__ === undefined;
var specs = [];

// Loaded from js/common.js
var config = require_config;

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

requirejs.config(config);

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
