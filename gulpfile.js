(function () {
    'use strict';

    var jshint = require('gulp-jshint');
    var gulp = require('gulp');
    var jasmine = require('gulp-jasmine');
    // lint this file in addition to js files.  Please add directories to this
    // as needed
    var lintSources = [
            'gulpfile.js',
            'analytics_dashboard/static/js/*.js',
            'analytics_dashboard/static/js/spec/*.js'];
    // add your test directories here
    var testSources = ['analytics_dashboard/static/spec/test.js'];

    gulp.task('lint', function() {
        return gulp.src(lintSources)
                .pipe(jshint())
                .pipe(jshint.reporter('default'));
    });

    gulp.task('test', function () {
        gulp.src(testSources)
            .pipe(jasmine());
    });

    // these are the default tasks when you run gulp
    gulp.task('default', ['lint', 'test']);

    // type 'gulp watch' to continuously run linting
    gulp.task('watch', function() {
        gulp.watch(lintSources, ['lint', 'test']);
    });

}());
