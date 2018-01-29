define(function(require) {
    'use strict';

    var URI = require('URI'),

        ListCollection = require('components/generic-list/common/collections/collection');

    describe('ListCollection', function() {
        var list,
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
            list = new ListCollection(null, {url: '/endpoint/'});
        });

        afterEach(function() {
            server.restore();
        });

        it('passes the expected url parameter to the collection fetch', function() {
            list.fetch();
            url = getUriForLastRequest(server);
            expect(url.path()).toEqual('/endpoint/');
        });

        it('passes the expected pagination querystring parameters', function() {
            list.setPage(1);
            url = getUriForLastRequest(server);
            expect(url.path()).toEqual('/endpoint/');
            expect(url.query(true)).toEqual({page: '1', page_size: '25'});
        });

        it('triggers an event when server gateway timeouts occur', function() {
            var spy = {eventCallback: function() {}};
            spyOn(spy, 'eventCallback');
            list.once('serverError', spy.eventCallback);
            list.fetch();
            lastRequest().respond(504, {}, '');
            expect(spy.eventCallback).toHaveBeenCalled();
        });

        describe('Backgrid Paginator shim', function() {
            it('implements hasPrevious', function() {
                list = new ListCollection({
                    num_pages: 2, count: 50, results: []
                }, {state: {currentPage: 2}, url: '/endpoint/', parse: true});
                expect(list.hasPreviousPage()).toBe(true);
                expect(list.hasPrevious()).toBe(true);
                list.state.currentPage = 1;
                expect(list.hasPreviousPage()).toBe(false);
                expect(list.hasPrevious()).toBe(false);
            });

            it('implements hasNext', function() {
                list = new ListCollection({
                    num_pages: 2, count: 50, results: []
                }, {state: {currentPage: 1}, url: '/endpoint/', parse: true});
                expect(list.hasNextPage()).toBe(true);
                expect(list.hasNext()).toBe(true);
                list.state.currentPage = 2;
                expect(list.hasNextPage()).toBe(false);
                expect(list.hasNext()).toBe(false);
            });
        });

        describe('Encoding State to a Query String', function() {
            it('encodes an empty state', function() {
                expect(list.getQueryString()).toBe('?page=1');
            });
            it('encodes the page number', function() {
                list.state.currentPage = 2;
                expect(list.getQueryString()).toBe('?page=2');
            });
            it('encodes the text search', function() {
                list.setFilterField('text_search', 'foo');
                expect(list.getQueryString()).toBe('?text_search=foo&page=1');
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
                list.setStateFromQueryString('');
                expect(list.state).toEqual(state);
                expect(list.getActiveFilterFields()).toEqual({});
            });
            it('decodes the page number', function() {
                state.currentPage = 2;
                list.setStateFromQueryString('page=2');
                expect(list.state).toEqual(state);
                expect(list.getActiveFilterFields()).toEqual({});
            });
            it('decodes the sort', function() {
                state.sortKey = 'username';
                state.order = 1;
                list.registerSortableField('username', 'Name (Username)');
                list.setStateFromQueryString('sortKey=username&order=desc');
                expect(list.state).toEqual(state);
                expect(list.getActiveFilterFields()).toEqual({});
            });
            it('decodes the text search', function() {
                list.setStateFromQueryString('text_search=foo');
                expect(list.state).toEqual(state);
                expect(list.getSearchString()).toEqual('foo');
            });
        });
    });
});
