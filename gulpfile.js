(function() {
    'use strict';

    var gulp = require('gulp'),
        Server = require('karma').Server,
        path = require('path'),
        extend = require('util')._extend, // eslint-disable-line no-underscore-dangle
        paths = {
            spec: [
                'analytics_dashboard/static/js/**/*.js',
                'analytics_dashboard/static/js/test/**/*.js',
                'analytics_dashboard/static/apps/**/*.js'
            ],
            templates: [
                'analytics_dashboard/analytics_dashboard/templates/analytics_dashboard/*.html',
                'analytics_dashboard/courses/templates/courses/*.html',
                'analytics_dashboard/templates/*.html'
            ],
            sass: ['analytics_dashboard/static/sass/*.scss'],
            karmaConf: 'karma.conf.js'
        };

    // kicks up karma to the tests once
    function runKarma(configFile, cb, options) {
        var defaultOptions = {
            configFile: path.resolve(configFile),
            singleRun: true,
            browsers: ['PhantomJS']
        };
        new Server(extend(defaultOptions, options), cb).start();
    }

    // this task runs the tests.  It doesn't give you very detailed results,
    // so you may need to run the jasmine test page directly:
    //      http://127.0.0.1:8000/static/js/test/spec-runner.html
    gulp.task('test', function(cb) {
        runKarma(paths.karmaConf, cb);
    });

    gulp.task('test-debug', function(cb) {
        runKarma(paths.karmaConf, cb, {
            singleRun: false,
            autoWatch: true,
            browsers: ['Chrome'],
            reporters: ['kjhtml']
        });
    });

    // these are the default tasks when you run gulp
    gulp.task('default', gulp.series('test'));

    // type 'gulp watch' to continuously run tests
    gulp.task('watch', function() {
        gulp.watch(paths.spec, ['test']);
    });
}());
