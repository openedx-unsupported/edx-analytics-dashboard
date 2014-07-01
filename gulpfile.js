(function () {
    'use strict';

    var jshint = require('gulp-jshint');
    var gulp = require('gulp');
    var karma = require('karma').server;
    var path = require('path');
    var browserSync = require('browser-sync');

    // lint this file in addition to js files.  Please add directories to this
    // as needed
    var paths = {
        // add your test directories here
        spec: ['analytics_dashboard/static/js/spec/specs/course-model-spec.js'],
        //spec: ['analytics_dashboard/static/js/spec/spec-runner.js'],
        lint: [
            'gulpfile.js',
            'analytics_dashboard/static/js/**/*.js',
            'analytics_dashboard/static/js/test/**/*.js'],
        templates: [
            'analytics_dashboard/courses/templates/courses/*.html',
            'analytics_dashboard/templates/*.html'
        ],
        sass: ['analytics_dashboard/static/sass/*.scss'],
        karamaConf: 'karma.conf.js'
    };

    // kicks up karma to the tests once
    function runKarma(configFile, cb) {
       karma.start({
          configFile: path.resolve(configFile),
          singleRun: true
       }, cb);
    }

    gulp.task('lint', function() {
        return gulp.src(paths.lint)
                .pipe(jshint())
                .pipe(jshint.reporter('default'));
    });

    // this task runs the tests.  It doesn't give you very detailed results,
    // so you may need to run the jasmine test page directly:
    //      http://127.0.0.1:8000/static/js/test/spec-runner.html
    gulp.task('test', function(cb) {
       runKarma(paths.karamaConf, cb);
    });

    // these are the default tasks when you run gulp
    gulp.task('default', ['lint', 'test']);

    // type 'gulp watch' to continuously run linting and tests
    gulp.task('watch', function() {
        gulp.watch(paths.spec, ['lint', 'test']);
    });

    // Proxy to django server (assuming that we're using port 8000 and
    // localhost)
    gulp.task('browser-sync', function() {
        // there is a little delay before reloading b/c the sass files need to
        // recompile, but we can't necessarily watch the generated directory
        // because django creates a new css file that browser-sync doesn't
        // know of and I can't figure out how to make it watch an entire
        // directory
        browserSync.init(null, {
            proxy: 'localhost:8000',
            files: paths.lint.concat(paths.templates).concat(paths.sass),
            reloadDelay: 1000
        });
    });

}());
