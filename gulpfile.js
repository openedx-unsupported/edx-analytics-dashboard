(function() {
    'use strict';

    var eslint = require('gulp-eslint'),
        gulp = require('gulp'),
        Server = require('karma').Server,
        path = require('path'),
        extend = require('util')._extend, // eslint-disable-line no-underscore-dangle
        paths = {
            spec: [
                'analytics_dashboard/static/js/**/*.js',
                'analytics_dashboard/static/js/test/**/*.js',
                'analytics_dashboard/static/apps/**/*.js'
            ],
            lint: [
                'gulpfile.js',
                'analytics_dashboard/static/js/**/*.js',
                'analytics_dashboard/static/js/test/**/*.js',
                'analytics_dashboard/static/apps/**/*.js',
                // TODO: Temporarily using different config file for these es6 modules.
                // Update this list to include modules newly converted to es6, and add them to lintES6.
                '!analytics_dashboard/static/apps/course-list/app/app.js',
                '!analytics_dashboard/static/apps/course-list/app/course-list-main.js'
            ],
            lintES6: [
                'analytics_dashboard/static/apps/course-list/app/app.js',
                'analytics_dashboard/static/apps/course-list/app/course-list-main.js'
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

    gulp.task('lint', function() {
        gulp.src(paths.lint)
            .pipe(eslint())
            .pipe(eslint.format())
            .pipe(eslint.failAfterError());

        return gulp.src(paths.lintES6)
            .pipe(eslint({configFile: '.es6-eslintrc.json'}))
            .pipe(eslint.format())
            .pipe(eslint.failAfterError());
    });

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
    gulp.task('default', ['test', 'lint']);

    // type 'gulp watch' to continuously run linting and tests
    gulp.task('watch', function() {
        gulp.watch(paths.spec, ['test', 'lint']);
    });
}());
