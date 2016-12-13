define(function(require) {
    'use strict';

    var EngagementTimelineModel = require('learners/common/models/engagement-timeline');

    describe('EngagementTimelineModel', function() {
        var server;

        beforeEach(function() {
            server = sinon.fakeServer.create();
        });

        afterEach(function() {
            server.restore();
        });

        it('sets its URL from the options parameter', function() {
            var model = new EngagementTimelineModel({}, {
                courseId: 'test/course/id',
                url: '/test-endpoint/'
            });
            expect(model.url()).toBe('/test-endpoint/?course_id=test%2Fcourse%2Fid');
        });

        it('handles AJAX failures', function(done) {
            var model = new EngagementTimelineModel({}, {
                    courseId: 'test/course/id',
                    url: '/test-endpoint/'
                }),
                responseJson = {error_message: 'Sorry, something went wrong'};
            spyOn(model, 'trigger');
            model.fetch().always(function() {
                expect(model.trigger).toHaveBeenCalledWith('serverError', 500, responseJson);
                done();
            });
            server.requests[server.requests.length - 1].respond(500, {}, JSON.stringify(responseJson));
        });
    });
});
