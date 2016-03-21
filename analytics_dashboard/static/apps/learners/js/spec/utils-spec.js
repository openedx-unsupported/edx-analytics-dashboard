require([
    'jquery',
    'learners/js/utils'
], function ($, LearnerUtils) {
    'use strict';

    describe('LearnerUtils', function () {
        describe('handleAjaxFailure', function () {
            var server;

            beforeEach(function () {
                jasmine.clock().install();
                server = sinon.fakeServer.create();  // jshint ignore:line
            });

            afterEach(function () {
                jasmine.clock().uninstall();
                server.restore();
            });

            it('does nothing when the request suceeds', function (done) {
                var spy = {trigger: function () {}};
                spyOn(spy, 'trigger');
                $.ajax('/resource/')
                    .fail(LearnerUtils.handleAjaxFailure.bind(spy))
                    .always(function () {
                        expect(spy.trigger).not.toHaveBeenCalled();
                        done();
                    });
                server.requests[server.requests.length - 1].respond(200);
            });

            it('triggers a server error event when the server responds with an error', function (done) {
                var fakeServerResponse = {error: 'something bad happened'},
                    spy = {trigger: function () {}};
                spyOn(spy, 'trigger');
                $.ajax({url: '/resource/', dataType: 'json'})
                    .fail(LearnerUtils.handleAjaxFailure.bind(spy))
                    .always(function () {
                        expect(spy.trigger).toHaveBeenCalledWith('serverError', 500, fakeServerResponse);
                        done();
                    });
                server.requests[server.requests.length - 1].respond(500, {}, JSON.stringify(fakeServerResponse));
            });

            it('triggers a network error event when the request fails', function (done) {
                var spy = {trigger: function () {}};
                spyOn(spy, 'trigger');
                $.ajax({url: '/resource/', timeout: 1})
                    .fail(LearnerUtils.handleAjaxFailure.bind(spy))
                    .always(function () {
                        expect(spy.trigger).toHaveBeenCalledWith('networkError', 'timeout');
                        done();
                    });
                jasmine.clock().tick(2);
            });
        });

        describe('inRange', function () {

            it('returns true when value is in range', function () {
                expect(LearnerUtils.inRange(1, [0, 2])).toBe(true);
                expect(LearnerUtils.inRange(10.5, [5, 11])).toBe(true);
                expect(LearnerUtils.inRange(44, [null, 45])).toBe(true);
                expect(LearnerUtils.inRange(59.3, [59, null])).toBe(true);
            });

            it('returns false when value is out of range', function () {
                expect(LearnerUtils.inRange(3, [0, 2])).toBe(false);
                expect(LearnerUtils.inRange(4.5, [5, 11])).toBe(false);
                expect(LearnerUtils.inRange(45, [null, 45])).toBe(false);
                expect(LearnerUtils.inRange(58.3, [59, null])).toBe(false);
            });

            it('throws error when bounds are null', function () {
                expect(function () {
                    LearnerUtils.inRange(1, [null, null]);
                }).toThrow(new Error('min and max range values cannot both be null (unbounded)'));
            });

        });

    });
});
