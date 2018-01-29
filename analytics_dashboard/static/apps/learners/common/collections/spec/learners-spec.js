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

        describe('Encoding State to a Query String', function() {
            it('encodes an empty state', function() {
                expect(learners.getQueryString()).toBe('?page=1');
            });
            it('encodes the page number', function() {
                learners.state.currentPage = 2;
                expect(learners.getQueryString()).toBe('?page=2');
            });
            it('encodes the sort state', function() {
                learners.state.sortKey = 'username';
                learners.state.order = 1;
                expect(learners.getQueryString()).toBe('?sortKey=username&order=desc&page=1');
            });
            it('encodes the text search', function() {
                learners.setFilterField('text_search', 'foo');
                expect(learners.getQueryString()).toBe('?text_search=foo&page=1');
            });
            it('encodes the filters', function() {
                var qstring, pageAfterFilters;
                learners.setFilterField('enrollment_mode', 'audit');
                learners.setFilterField('cohort', 'group1');
                // order of filter fields in query string is not defined
                qstring = learners.getQueryString();
                pageAfterFilters = (qstring === '?enrollment_mode=audit&cohort=group1&page=1' ||
                                    qstring === '?cohort=group1&enrollment_mode=audit&page=1');
                expect(pageAfterFilters).toBe(true);
            });
        });

        describe('Decoding Query String to a State', function() {
            var state = {};
            beforeEach(function() {
                state = {
                    firstPage: 1,
                    lastPage: null,
                    currentPage: 1,
                    pageSize: 25,
                    totalPages: null,
                    totalRecords: null,
                    sortKey: null,
                    order: -1
                };
            });
            it('decodes an empty query string', function() {
                learners.setStateFromQueryString('');
                expect(learners.state).toEqual(state);
                expect(learners.getActiveFilterFields()).toEqual({});
            });
            it('decodes the page number', function() {
                state.currentPage = 2;
                learners.setStateFromQueryString('page=2');
                expect(learners.state).toEqual(state);
                expect(learners.getActiveFilterFields()).toEqual({});
            });
            it('decodes the sort', function() {
                state.sortKey = 'username';
                state.order = 1;
                learners.setStateFromQueryString('sortKey=username&order=desc');
                expect(learners.state).toEqual(state);
                expect(learners.getActiveFilterFields()).toEqual({});
            });
            it('decodes the text search', function() {
                learners.setStateFromQueryString('text_search=foo');
                expect(learners.state).toEqual(state);
                expect(learners.getSearchString()).toEqual('foo');
            });
            it('decodes the filters', function() {
                learners.setStateFromQueryString('enrollment_mode=audit&cohort=group1');
                expect(learners.state).toEqual(state);
                expect(learners.getActiveFilterFields()).toEqual({enrollment_mode: 'audit', cohort: 'group1'});
            });
        });
    });
});
