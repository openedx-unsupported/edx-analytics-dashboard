define((require) => {
  'use strict';

  const $ = require('jquery');

  const ListUtils = require('components/utils/utils');

  describe('ListUtils', () => {
    describe('handleAjaxFailure', () => {
      let server;

      beforeEach(() => {
        jasmine.clock().install();
        server = sinon.fakeServer.create();
      });

      afterEach(() => {
        jasmine.clock().uninstall();
        server.restore();
      });

      it('does nothing when the request suceeds', (done) => {
        const spy = { trigger() {} };
        spyOn(spy, 'trigger');
        $.ajax('/resource/')
          .fail(ListUtils.handleAjaxFailure.bind(spy))
          .always(() => {
            expect(spy.trigger).not.toHaveBeenCalled();
            done();
          });
        server.requests[server.requests.length - 1].respond(200);
      });

      it('triggers a server error event when the server responds with an error', (done) => {
        const fakeServerResponse = { error: 'something bad happened' };
        const spy = { trigger() {} };
        spyOn(spy, 'trigger');
        $.ajax({ url: '/resource/', dataType: 'json' })
          .fail(ListUtils.handleAjaxFailure.bind(spy))
          .always(() => {
            expect(spy.trigger).toHaveBeenCalledWith('serverError', 500, fakeServerResponse);
            done();
          });
        server.requests[server.requests.length - 1].respond(500, {}, JSON.stringify(fakeServerResponse));
      });

      it('triggers a network error event when the request fails', (done) => {
        const spy = { trigger() {} };
        spyOn(spy, 'trigger');
        $.ajax({ url: '/resource/', timeout: 1 })
          .fail(ListUtils.handleAjaxFailure.bind(spy))
          .always(() => {
            expect(spy.trigger).toHaveBeenCalledWith('networkError', 'timeout');
            done();
          });
        jasmine.clock().tick(2);
      });
    });
  });
});
