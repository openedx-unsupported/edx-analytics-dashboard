define(function(require) {
    'use strict';

    var URI = require('URI'),

        LearnerCollection = require('learners/common/collections/learners');

    describe('LearnerCollection', function() {
        var courseId = 'org/course/run',
            learners,
            server,
            url,
            lastRequest,
            getUriForLastRequest;

        lastRequest = function() {
            return server.requests[server.requests.length - 1];
        };

        getUriForLastRequest = function() {
            return new URI(lastRequest().url);
        };

        beforeEach(function() {
            server = sinon.fakeServer.create();
            learners = new LearnerCollection(null, {url: '/endpoint/', courseId: courseId});
        });

        afterEach(function() {
            server.restore();
        });

        it('passes the required course_id querystring parameter', function() {
            learners.fetch();
            url = getUriForLastRequest(server);
            expect(url.path()).toEqual('/endpoint/');
            expect(url.query(true)).toEqual(jasmine.objectContaining({course_id: courseId}));
        });

        it('passes the expected pagination querystring parameters', function() {
            learners.setPage(1);
            url = getUriForLastRequest(server);
            expect(url.path()).toEqual('/endpoint/');
            expect(url.query(true)).toEqual({page: '1', page_size: '25', course_id: courseId});
        });

        it('can add and remove filters', function() {
            learners.setFilterField('segments', ['inactive', 'unenrolled']);
            learners.setFilterField('cohort', 'Cool Cohort');
            learners.refresh();
            url = getUriForLastRequest(server);
            expect(url.path()).toEqual('/endpoint/');
            expect(url.query(true)).toEqual({
                page: '1',
                page_size: '25',
                course_id: courseId,
                segments: 'inactive,unenrolled',
                cohort: 'Cool Cohort'
            });
            learners.unsetAllFilterFields();
            learners.refresh();
            url = getUriForLastRequest(server);
            expect(url.path()).toEqual('/endpoint/');
            expect(url.query(true)).toEqual({
                page: '1',
                page_size: '25',
                course_id: courseId
            });
        });

        describe('Sorting', function() {
            var testSorting = function(sortField) {
                learners.setSortField(sortField);
                learners.refresh();
                url = getUriForLastRequest(server);
                expect(url.path()).toEqual('/endpoint/');
                expect(url.query(true)).toEqual({
                    page: '1',
                    page_size: '25',
                    course_id: courseId,
                    order_by: sortField,
                    sort_order: 'asc'
                });
                learners.flipSortDirection();
                learners.refresh();
                url = getUriForLastRequest(server);
                expect(url.query(true)).toEqual({
                    page: '1',
                    page_size: '25',
                    course_id: courseId,
                    order_by: sortField,
                    sort_order: 'desc'
                });
            };

            it('can sort by username', function() {
                testSorting('username');
            });

            it('can sort by problems_attempted', function() {
                testSorting('problems_attempted');
            });

            it('can sort by problems_completed', function() {
                testSorting('problems_completed');
            });

            it('can sort by videos_viewed', function() {
                testSorting('videos_viewed');
            });

            it('can sort by problems_attempted_per_completed', function() {
                testSorting('problems_attempted_per_completed');
            });

            it('can sort by discussion_contributions', function() {
                testSorting('discussion_contributions');
            });
        });

        it('can do a full text search', function() {
            learners.setSearchString('search example');
            learners.refresh();
            url = getUriForLastRequest(server);
            expect(url.path()).toEqual('/endpoint/');
            expect(url.query(true)).toEqual({
                page: '1',
                page_size: '25',
                course_id: courseId,
                text_search: 'search example'
            });
            learners.unsetSearchString();
            learners.refresh();
            url = getUriForLastRequest(server);
            expect(url.query(true)).toEqual({
                page: '1',
                page_size: '25',
                course_id: courseId
            });
        });

        it('can filter, sort, and search all at once', function() {
            learners.setFilterField('ignore_segments', ['highly_engaged', 'unenrolled']);
            learners.setSortField('videos_viewed');
            learners.setSearchString('search example');
            learners.refresh();
            url = getUriForLastRequest(server);
            expect(url.path()).toEqual('/endpoint/');
            expect(url.query(true)).toEqual({
                page: '1',
                page_size: '25',
                course_id: courseId,
                text_search: 'search example',
                ignore_segments: 'highly_engaged,unenrolled',
                order_by: 'videos_viewed',
                sort_order: 'asc'
            });
        });

        it('triggers an event when server gateway timeouts occur', function() {
            var spy = {eventCallback: function() {}};
            spyOn(spy, 'eventCallback');
            learners.once('serverError', spy.eventCallback);
            learners.fetch();
            lastRequest().respond(504, {}, '');
            expect(spy.eventCallback).toHaveBeenCalled();
        });

        describe('Backgrid Paginator shim', function() {
            it('implements hasPrevious', function() {
                learners = new LearnerCollection({
                    num_pages: 2, count: 50, results: []
                }, {state: {currentPage: 2}, url: '/endpoint/', courseId: courseId, parse: true});
                expect(learners.hasPreviousPage()).toBe(true);
                expect(learners.hasPrevious()).toBe(true);
                learners.state.currentPage = 1;
                expect(learners.hasPreviousPage()).toBe(false);
                expect(learners.hasPrevious()).toBe(false);
            });

            it('implements hasNext', function() {
                learners = new LearnerCollection({
                    num_pages: 2, count: 50, results: []
                }, {state: {currentPage: 1}, url: '/endpoint/', courseId: courseId, parse: true});
                expect(learners.hasNextPage()).toBe(true);
                expect(learners.hasNext()).toBe(true);
                learners.state.currentPage = 2;
                expect(learners.hasNextPage()).toBe(false);
                expect(learners.hasNext()).toBe(false);
            });
        });
    });
});
