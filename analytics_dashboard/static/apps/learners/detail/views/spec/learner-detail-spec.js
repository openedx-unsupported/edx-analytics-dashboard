define(function(require) {
    'use strict';

    var EngagementTimelineModel = require('learners/common/models/engagement-timeline'),
        LearnerDetailView = require('learners/detail/views/learner-detail'),
        LearnerModel = require('learners/common/models/learner'),
        TrackingModel = require('models/tracking-model'),
        Utils = require('utils/utils'),
        _ = require('underscore');

    describe('LearnerDetailView', function() {
        var fixtureClass = '.learner-detail-fixture';

        beforeEach(function() {
            setFixtures('<div class="' + fixtureClass.slice(1) + '"></div>');
        });

        it('renders a loading view first', function() {
            var engagementTimelineModel = new EngagementTimelineModel(),
                detailView = new LearnerDetailView({
                    learnerModel: new LearnerModel(),
                    engagementTimelineModel: engagementTimelineModel,
                    el: fixtureClass
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

        describe('managing the engagement timeline', function() {
            var server;

            beforeEach(function() {
                server = sinon.fakeServer.create();
            });

            afterEach(function() {
                server.restore();
            });

            it('renders a timeline', function() {
                var engagementTimelineModel,
                    detailView;

                engagementTimelineModel = new EngagementTimelineModel({
                    days: [{
                        date: '2016-01-01',
                        discussion_contributions: 1,
                        problems_attempted: 1,
                        problems_completed: 1,
                        videos_viewed: 1
                    }]
                });
                detailView = new LearnerDetailView({
                    learnerModel: new LearnerModel(),
                    engagementTimelineModel: engagementTimelineModel,
                    el: fixtureClass
                });
                detailView.render().onBeforeShow();
                expect(detailView.$('.loading-container')).not.toExist();
                expect(detailView.$('.learner-engagement-timeline')).toExist();
                expect(detailView.$('.learner-accessed')).toContainText(
                    Utils.formatDate(_(engagementTimelineModel.get('days')).last().date)
                );
            });

            it('renders a table', function() {
                var engagementTimelineModel,
                    detailView;

                engagementTimelineModel = new EngagementTimelineModel({
                    days: [{
                        date: '2016-01-01',
                        discussion_contributions: 1,
                        problems_attempted: 1,
                        problems_completed: 1,
                        videos_viewed: 1
                    }]
                });
                detailView = new LearnerDetailView({
                    learnerModel: new LearnerModel(),
                    engagementTimelineModel: engagementTimelineModel,
                    el: fixtureClass
                });
                detailView.render().onBeforeShow();
                expect(detailView.$('.table-loading-container')).not.toExist();
                expect(detailView.$('.learner-engagement-table')).toExist();
            });

            it('handles 404s from the timeline endpoint', function() {
                var engagementTimelineModel,
                    detailView;
                engagementTimelineModel = new EngagementTimelineModel();
                detailView = new LearnerDetailView({
                    learnerModel: new LearnerModel(),
                    engagementTimelineModel: engagementTimelineModel,
                    el: fixtureClass
                });
                detailView.render().onBeforeShow();
                expect(detailView.$('#table-section')).toExist();
                engagementTimelineModel.fetch();
                server.requests[server.requests.length - 1].respond(404, {}, '');
                expect(detailView.$('[role="alert"]')).toExist();
                expect(detailView.$('#table-section')).not.toExist();
            });
        });

        describe('basic user profile', function() {
            var learnerModel,
                server;

            beforeEach(function() {
                server = sinon.fakeServer.create();
                learnerModel = new LearnerModel({
                    course_id: 'test/course/1',
                    username: 'dummy-user'
                });
                learnerModel.urlRoot = 'test-endpoint';
            });

            afterEach(function() {
                server.restore();
            });

            it('renders the profile', function() {
                var detailView = new LearnerDetailView({
                    learnerModel: learnerModel,
                    engagementTimelineModel: new EngagementTimelineModel(),
                    el: fixtureClass
                });

                learnerModel.set({
                    name: 'Spider Plant',
                    email: 'spider@plant.com',
                    enrollment_mode: 'honor',
                    cohort: 'Shade Tolerant'
                });

                detailView.render().onBeforeShow();
                expect(detailView.$('.learner-username')).toContainText('dummy-user');
                expect(detailView.$('.learner-name')).toContainText('Spider Plant');
                expect(detailView.$('.learner-enrollment')).toContainText('honor');
                expect(detailView.$('.learner-cohort')).toContainText('Shade Tolerant');
                expect(detailView.$('.learner-accessed')).toContainText('n/a');
                expect(detailView.$('.learner-email')).toContainText('spider@plant.com');
            });

            it('handles 404s from the learner endpoint', function() {
                var detailView;

                detailView = new LearnerDetailView({
                    learnerModel: learnerModel,
                    engagementTimelineModel: new EngagementTimelineModel(),
                    el: fixtureClass
                });

                detailView.render().onBeforeShow();
                learnerModel.fetch();
                spyOn(detailView, 'triggerMethod');
                server.requests[server.requests.length - 1].respond(404, {}, '');
                expect(detailView.triggerMethod)
                    .toHaveBeenCalledWith('learnerUnavailable', jasmine.any(Object));
            });

            it('triggers a tracking event on email link click', function() {
                var trackingModel = new TrackingModel(),
                    detailView = new LearnerDetailView({
                        learnerModel: learnerModel,
                        engagementTimelineModel: new EngagementTimelineModel(),
                        el: fixtureClass,
                        trackingModel: trackingModel
                    }),
                    triggerSpy = spyOn(trackingModel, 'trigger');

                trackingModel.set({
                    segmentApplicationId: 'foobar',
                    page: 'learner_details'
                });
                learnerModel.set({
                    email: 'spider@plant.com'
                });

                detailView.render().onBeforeShow();
                detailView.$('.learner-email a').click();

                expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.learner.email_link_clicked', {});
            });
        });
    });
});
