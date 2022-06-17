define((require) => {
  'use strict';

  const URI = require('URI');

  const ListCollection = require('components/generic-list/common/collections/collection');

  describe('ListCollection', () => {
    let list;
    let server;
    let url;

    const lastRequest = function () {
      return server.requests[server.requests.length - 1];
    };

    const getUriForLastRequest = function () {
      return new URI(lastRequest().url);
    };

    beforeEach(() => {
      server = sinon.fakeServer.create();
      list = new ListCollection(null, { url: '/endpoint/' });
    });

    afterEach(() => {
      server.restore();
    });

    it('passes the expected url parameter to the collection fetch', () => {
      list.fetch();
      url = getUriForLastRequest(server);
      expect(url.path()).toEqual('/endpoint/');
    });

    it('passes the expected pagination querystring parameters', () => {
      list.setPage(1);
      url = getUriForLastRequest(server);
      expect(url.path()).toEqual('/endpoint/');
      expect(url.query(true)).toEqual({ page: '1', page_size: '25' });
    });

    it('triggers an event when server gateway timeouts occur', () => {
      const spy = { eventCallback() {} };
      spyOn(spy, 'eventCallback');
      list.once('serverError', spy.eventCallback);
      list.fetch();
      lastRequest().respond(504, {}, '');
      expect(spy.eventCallback).toHaveBeenCalled();
    });

    describe('Backgrid Paginator shim', () => {
      it('implements hasPrevious', () => {
        list = new ListCollection({
          num_pages: 2, count: 50, results: [],
        }, { state: { currentPage: 2 }, url: '/endpoint/', parse: true });
        expect(list.hasPreviousPage()).toBe(true);
        expect(list.hasPrevious()).toBe(true);
        list.state.currentPage = 1;
        expect(list.hasPreviousPage()).toBe(false);
        expect(list.hasPrevious()).toBe(false);
      });

      it('implements hasNext', () => {
        list = new ListCollection({
          num_pages: 2, count: 50, results: [],
        }, { state: { currentPage: 1 }, url: '/endpoint/', parse: true });
        expect(list.hasNextPage()).toBe(true);
        expect(list.hasNext()).toBe(true);
        list.state.currentPage = 2;
        expect(list.hasNextPage()).toBe(false);
        expect(list.hasNext()).toBe(false);
      });
    });

    describe('Encoding State to a Query String', () => {
      it('encodes an empty state', () => {
        expect(list.getQueryString()).toBe('?page=1');
      });
      it('encodes the page number', () => {
        list.state.currentPage = 2;
        expect(list.getQueryString()).toBe('?page=2');
      });
      it('encodes the text search', () => {
        list.setFilterField('text_search', 'foo');
        expect(list.getQueryString()).toBe('?text_search=foo&page=1');
      });
    });

    describe('Decoding Query String to a State', () => {
      let state = {};
      beforeEach(() => {
        state = {
          firstPage: 1,
          lastPage: null,
          currentPage: 1,
          pageSize: 25,
          totalPages: null,
          totalRecords: null,
          sortKey: null,
          order: -1,
        };
      });
      it('decodes an empty query string', () => {
        list.setStateFromQueryString('');
        expect(list.state).toEqual(state);
        expect(list.getActiveFilterFields()).toEqual({});
      });
      it('decodes the page number', () => {
        state.currentPage = 2;
        list.setStateFromQueryString('page=2');
        expect(list.state).toEqual(state);
        expect(list.getActiveFilterFields()).toEqual({});
      });
      it('decodes the sort', () => {
        state.sortKey = 'username';
        state.order = 1;
        list.registerSortableField('username', 'Name (Username)');
        list.setStateFromQueryString('sortKey=username&order=desc');
        expect(list.state).toEqual(state);
        expect(list.getActiveFilterFields()).toEqual({});
      });
      it('decodes the text search', () => {
        list.setStateFromQueryString('text_search=foo');
        expect(list.state).toEqual(state);
        expect(list.getSearchString()).toEqual('foo');
      });
    });
  });
});
