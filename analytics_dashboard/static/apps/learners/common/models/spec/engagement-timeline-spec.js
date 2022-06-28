define((require) => {
  'use strict';

  const EngagementTimelineModel = require('learners/common/models/engagement-timeline');

  describe('EngagementTimelineModel', () => {
    let server;

    beforeEach(() => {
      server = sinon.fakeServer.create();
    });

    afterEach(() => {
      server.restore();
    });

    it('sets its URL from the options parameter', () => {
      const model = new EngagementTimelineModel({}, {
        courseId: 'test/course/id',
        url: '/test-endpoint/',
      });
      expect(model.url()).toBe('/test-endpoint/?course_id=test%2Fcourse%2Fid');
    });

    it('handles AJAX failures', (done) => {
      const model = new EngagementTimelineModel({}, {
        courseId: 'test/course/id',
        url: '/test-endpoint/',
      });
      const responseJson = { error_message: 'Sorry, something went wrong' };
      spyOn(model, 'trigger');
      model.fetch().always(() => {
        expect(model.trigger).toHaveBeenCalledWith('serverError', 500, responseJson);
        done();
      });
      server.requests[server.requests.length - 1].respond(500, {}, JSON.stringify(responseJson));
    });
  });
});
