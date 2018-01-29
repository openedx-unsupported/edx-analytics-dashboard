define(function(require) {
    'use strict';

    var $ = require('jquery'),

        ListUtils = require('components/utils/utils');

    describe('ListUtils', function() {
        describe('handleAjaxFailure', function() {
            var server;

            beforeEach(function() {
                jasmine.clock().install();
                server = sinon.fakeServer.create();
            });

            afterEach(function() {
                jasmine.clock().uninstall();
                server.restore();
            });

            it('does nothing when the request suceeds', function(done) {
                var spy = {trigger: function() {}};
                spyOn(spy, 'trigger');
                $.ajax('/resource/')
                    .fail(ListUtils.handleAjaxFailure.bind(spy))
                    .always(function() {
                        expect(spy.trigger).not.toHaveBeenCalled();
                        done();
                    });
                server.requests[server.requests.length - 1].respond(200);
            });

            it('triggers a server error event when the server responds with an error', function(done) {
                var fakeServerResponse = {error: 'something bad happened'},
                    spy = {trigger: function() {}};
                spyOn(spy, 'trigger');
                $.ajax({url: '/resource/', dataType: 'json'})
                    .fail(ListUtils.handleAjaxFailure.bind(spy))
                    .always(function() {
                        expect(spy.trigger).toHaveBeenCalledWith('serverError', 500, fakeServerResponse);
                        done();
                    });
                server.requests[server.requests.length - 1].respond(500, {}, JSON.stringify(fakeServerResponse));
            });

            it('triggers a network error event when the request fails', function(done) {
                var spy = {trigger: function() {}};
                spyOn(spy, 'trigger');
                $.ajax({url: '/resource/', timeout: 1})
                    .fail(ListUtils.handleAjaxFailure.bind(spy))
                    .always(function() {
                        expect(spy.trigger).toHaveBeenCalledWith('networkError', 'timeout');
                        done();
                    });
                jasmine.clock().tick(2);
            });
        });
    });
});
