define((require) => {
  'use strict';

  const EngagementTimelineModel = require('learners/common/models/engagement-timeline');
  const LearnerDetailView = require('learners/detail/views/learner-detail');
  const LearnerModel = require('learners/common/models/learner');
  const TrackingModel = require('models/tracking-model');
  const Utils = require('utils/utils');
  const _ = require('underscore');

  describe('LearnerDetailView', () => {
    const fixtureClass = '.learner-detail-fixture';

    beforeEach(() => {
      setFixtures(`<div class="${fixtureClass.slice(1)}"></div>`);
    });

    it('renders a loading view first', () => {
      const engagementTimelineModel = new EngagementTimelineModel();
      const detailView = new LearnerDetailView({
        learnerModel: new LearnerModel(),
        engagementTimelineModel,
        el: fixtureClass,
      });

      detailView.render().onBeforeShow();
      expect(detailView.$('.chart-loading-container')).toExist();
      expect(detailView.$('.table-loading-container')).toExist();
      expect(detailView.$('.learner-engagement-timeline')).not.toExist();
      expect(detailView.$('.learner-engagement-table')).not.toExist();

      engagementTimelineModel.trigger('sync');
      expect(detailView.$('.loading-container')).not.toExist();
      expect(detailView.$('.learner-engagement-timeline')).toExist();
    });

    describe('managing the engagement timeline', () => {
      let server;

      beforeEach(() => {
        server = sinon.fakeServer.create();
      });

      afterEach(() => {
        server.restore();
      });

      it('renders a timeline', () => {
        const engagementTimelineModel = new EngagementTimelineModel({
          days: [{
            date: '2016-01-01',
            discussion_contributions: 1,
            problems_attempted: 1,
            problems_completed: 1,
            videos_viewed: 1,
          }],
        });
        const detailView = new LearnerDetailView({
          learnerModel: new LearnerModel(),
          engagementTimelineModel,
          el: fixtureClass,
        });
        detailView.render().onBeforeShow();
        expect(detailView.$('.loading-container')).not.toExist();
        expect(detailView.$('.learner-engagement-timeline')).toExist();
        expect(detailView.$('.learner-accessed')).toContainText(
          Utils.formatDate(_(engagementTimelineModel.get('days')).last().date),
        );
      });

      it('renders a table', () => {
        const engagementTimelineModel = new EngagementTimelineModel({
          days: [{
            date: '2016-01-01',
            discussion_contributions: 1,
            problems_attempted: 1,
            problems_completed: 1,
            videos_viewed: 1,
          }],
        });
        const detailView = new LearnerDetailView({
          learnerModel: new LearnerModel(),
          engagementTimelineModel,
          el: fixtureClass,
        });
        detailView.render().onBeforeShow();
        expect(detailView.$('.table-loading-container')).not.toExist();
        expect(detailView.$('.learner-engagement-table')).toExist();
      });

      it('handles 404s from the timeline endpoint', () => {
        const engagementTimelineModel = new EngagementTimelineModel();
        const detailView = new LearnerDetailView({
          learnerModel: new LearnerModel(),
          engagementTimelineModel,
          el: fixtureClass,
        });
        detailView.render().onBeforeShow();
        expect(detailView.$('#table-section')).toExist();
        engagementTimelineModel.fetch();
        server.requests[server.requests.length - 1].respond(404, {}, '');
        expect(detailView.$('[role="alert"]')).toExist();
        expect(detailView.$('#table-section')).not.toExist();
      });
    });

    describe('basic user profile', () => {
      let learnerModel;
      let server;

      beforeEach(() => {
        server = sinon.fakeServer.create();
        learnerModel = new LearnerModel({
          course_id: 'test/course/1',
          username: 'dummy-user',
        });
        learnerModel.urlRoot = 'test-endpoint';
      });

      afterEach(() => {
        server.restore();
      });

      it('renders the profile', () => {
        const detailView = new LearnerDetailView({
          learnerModel,
          engagementTimelineModel: new EngagementTimelineModel(),
          el: fixtureClass,
        });

        learnerModel.set({
          name: 'Spider Plant',
          email: 'spider@plant.com',
          enrollment_mode: 'honor',
          cohort: 'Shade Tolerant',
        });

        detailView.render().onBeforeShow();
        expect(detailView.$('.learner-username')).toContainText('dummy-user');
        expect(detailView.$('.learner-name')).toContainText('Spider Plant');
        expect(detailView.$('.learner-enrollment')).toContainText('honor');
        expect(detailView.$('.learner-cohort')).toContainText('Shade Tolerant');
        expect(detailView.$('.learner-accessed')).toContainText('n/a');
        expect(detailView.$('.learner-email')).toContainText('spider@plant.com');
      });

      it('handles 404s from the learner endpoint', () => {
        const detailView = new LearnerDetailView({
          learnerModel,
          engagementTimelineModel: new EngagementTimelineModel(),
          el: fixtureClass,
        });

        detailView.render().onBeforeShow();
        learnerModel.fetch();
        spyOn(detailView, 'triggerMethod');
        server.requests[server.requests.length - 1].respond(404, {}, '');
        expect(detailView.triggerMethod)
          .toHaveBeenCalledWith('learnerUnavailable', jasmine.any(Object));
      });

      it('triggers a tracking event on email link click', () => {
        const trackingModel = new TrackingModel();
        const detailView = new LearnerDetailView({
          learnerModel,
          engagementTimelineModel: new EngagementTimelineModel(),
          el: fixtureClass,
          trackingModel,
        });
        const triggerSpy = spyOn(trackingModel, 'trigger');

        trackingModel.set({
          segmentApplicationId: 'foobar',
          page: 'learner_details',
        });
        learnerModel.set({
          email: 'spider@plant.com',
        });

        detailView.render().onBeforeShow();
        detailView.$('.learner-email a').click();

        expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.learner.email_link_clicked', {});
      });
    });
  });
});
