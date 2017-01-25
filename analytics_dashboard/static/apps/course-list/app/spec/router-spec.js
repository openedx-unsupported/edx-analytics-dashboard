define(function(require) {
    'use strict';

    var Backbone = require('backbone'),
        CourseListCollection = require('course-list/common/collections/course-list'),
        CourseListController = require('course-list/app/controller'),
        CourseListRouter = require('course-list/app/router'),
        PageModel = require('components/generic-list/common/models/page');

    describe('CourseListRouter', function() {
        beforeEach(function() {
            Backbone.history.start({silent: true});
            this.course = {
                last_updated: new Date(2016, 1, 28)
            };
            this.collection = new CourseListCollection([this.course]);
            this.controller = new CourseListController({
                courseListCollection: this.collection,
                pageModel: new PageModel()
            });
            spyOn(this.controller, 'showCourseListPage').and.stub();
            spyOn(this.controller, 'showNotFoundPage').and.stub();
            spyOn(this.controller, 'onShowPage').and.stub();
            this.router = new CourseListRouter({
                controller: this.controller
            });
        });

        afterEach(function() {
            // Clear previous route
            this.router.navigate('');
            Backbone.history.stop();
        });

        it('triggers a showPage event for pages beginning with "show"', function() {
            this.router.navigate('foo', {trigger: true});
            expect(this.controller.onShowPage).toHaveBeenCalled();
            this.router.navigate('/', {trigger: true});
            expect(this.controller.onShowPage).toHaveBeenCalled();
        });

        describe('showCourseListPage', function() {
            beforeEach(function() {
                // Backbone won't trigger a route unless we were on a previous url
                this.router.navigate('initial-fragment', {trigger: false});
            });

            it('should trigger on an empty URL fragment', function() {
                this.router.navigate('', {trigger: true});
                expect(this.controller.showCourseListPage).toHaveBeenCalled();
            });

            it('should trigger on a single forward slash', function() {
                this.router.navigate('/', {trigger: true});
                expect(this.controller.showCourseListPage).toHaveBeenCalled();
            });

            it('should trigger on a URL fragment with a querystring', function() {
                var querystring = 'text_search=some_course';
                this.router.navigate('?' + querystring, {trigger: true});
                expect(this.controller.showCourseListPage).toHaveBeenCalledWith(querystring, null);
            });
        });

        describe('showNotFoundPage', function() {
            it('should trigger on unmatched URLs', function() {
                this.router.navigate('this/does/not/match', {trigger: true});
                expect(this.controller.showNotFoundPage).toHaveBeenCalledWith('this/does/not/match', null);
            });
        });

        it('URL fragment is updated on CourseListCollection loaded', function(done) {
            this.collection.state.currentPage = 2;
            this.collection.once('loaded', function() {
                expect(Backbone.history.getFragment()).toBe('?sortKey=catalog_course_title&order=asc&page=2');
                done();
            });
            this.collection.trigger('loaded');
        });

        it('URL fragment is updated on CourseListCollection refresh', function(done) {
            this.collection.state.currentPage = 2;
            this.collection.once('backgrid:refresh', function() {
                expect(Backbone.history.getFragment()).toBe('?sortKey=catalog_course_title&order=asc&page=2');
                done();
            });
            this.collection.trigger('backgrid:refresh');
        });
    });
});
