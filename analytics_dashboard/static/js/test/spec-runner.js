/**
 * This is where your tests go.  It should happen automatically when you
 * add files to the karma configuration.
 */
(function() {
    'use strict';

    var isBrowser = window.__karma__ === undefined, // eslint-disable-line no-underscore-dangle
        specs = [],
        config = {};

    // Two execution paths: browser or gulp
    if (isBrowser) {
        // The browser cannot read directories, so all files must be enumerated below.
        specs = [
            config.baseUrl + 'js/spec/specs/attribute-view-spec.js',
            config.baseUrl + 'js/spec/specs/course-model-spec.js',
            config.baseUrl + 'js/spec/specs/data-table-spec.js',
            config.baseUrl + 'js/spec/specs/tracking-model-spec.js',
            config.baseUrl + 'js/spec/specs/trends-view-spec.js',
            config.baseUrl + 'js/spec/specs/world-map-view-spec.js',
            config.baseUrl + 'js/spec/specs/tracking-view-spec.js',
            config.baseUrl + 'js/spec/specs/utils-spec.js',
            config.baseUrl + 'js/spec/specs/globalization-spec.js',
            config.baseUrl + 'js/spec/specs/announcement-view-spec.js'
        ];
    } else {
        // the Insights application loads gettext identity library via django, thus
        // components reference gettext globally so a shim is added here to reflect
        // the text so tests can be run if modules reference gettext
        if (!window.gettext) {
            window.gettext = function(text) {
                return text;
            };
        }

        if (!window.ngettext) {
            window.ngettext = function(singularString, pluralString, count) {
                if (count === 1) {
                    return singularString;
                } else {
                    return pluralString;
                }
            };
        }

        // you can automatically get the test files using karma's configs
        Object.keys(window.__karma__.files).forEach(function(file) { // eslint-disable-line no-underscore-dangle
            if (/spec\.js$/.test(file)) {
                specs.push(file);
            }
        });
        // This is where karma puts the files
        config.baseUrl = '/base/analytics_dashboard/static/';

        // Karma lets you list the test files here
        config.deps = specs;
        config.callback = window.__karma__.start; // eslint-disable-line no-underscore-dangle
    }

    requirejs.config(config);

    // the browser needs to kick off jasmine.  The gulp task does it through
    // node
    if (isBrowser) {
        // jasmine 2.0 needs boot.js to run, which loads on a window load, so this is
        // a hack
        // http://stackoverflow.com/questions/19240302/does-jasmine-2-0-really-not-work-with-require-js
        require(['boot'], function() {
            require(specs,
                function() {
                    window.onload();
                });
        });
    }
}());
