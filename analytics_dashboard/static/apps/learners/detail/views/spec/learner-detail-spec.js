define(function (require) {
    'use strict';

    var EngagementTimelineModel = require('learners/common/models/engagement-timeline'),
        LearnerDetailView = require('learners/detail/views/learner-detail');

    describe('LearnerDetailView', function () {
        var fixtureClass = '.learner-detail-fixture';

        beforeEach(function () {
            setFixtures('<div class="' + fixtureClass.slice(1) + '"></div>');
        });

        it('renders a loading view first', function () {
            var engagementTimelineModel = new EngagementTimelineModel(),
                detailView = new LearnerDetailView({
                    engagementTimelineModel: engagementTimelineModel,
                    el: fixtureClass
                });

            detailView.render().onBeforeShow();
            expect(detailView.$('.loading-container')).toExist();
            expect(detailView.$('.learner-engagement-timeline')).not.toExist();

            engagementTimelineModel.trigger('sync');
            expect(detailView.$('.loading-container')).not.toExist();
            expect(detailView.$('.learner-engagement-timeline')).toExist();
        });

        describe('managing the engagement timeline', function () {
            var server;

            beforeEach(function () {
                server = sinon.fakeServer.create();
            });

            afterEach(function () {
                server.restore();
            });

            it('renders a timeline', function () {
                var engagementTimelineModel,
                    detailView;

                engagementTimelineModel = new EngagementTimelineModel({
                    days: [{
                        date: '2016-01-01',
                        discussions_contributed: 1,
                        problems_attempted: 1,
                        problems_completed: 1,
                        videos_viewed: 1
                    }]
                });
                detailView = new LearnerDetailView({
                    engagementTimelineModel: engagementTimelineModel,
                    el: fixtureClass
                });
                detailView.render().onBeforeShow();
                expect(detailView.$('.loading-container')).not.toExist();
                expect(detailView.$('.learner-engagement-timeline')).toExist();
            });

            it('handles 404s from the timeline endpoint', function () {
                var engagementTimelineModel,
                    detailView;
                engagementTimelineModel = new EngagementTimelineModel();
                detailView = new LearnerDetailView({
                    engagementTimelineModel: engagementTimelineModel,
                    el: fixtureClass
                });
                detailView.render().onBeforeShow();
                engagementTimelineModel.fetch();
                spyOn(detailView, 'triggerMethod');
                server.requests[server.requests.length - 1].respond(404, {}, '');
                expect(detailView.triggerMethod).toHaveBeenCalledWith('appWarning', jasmine.any(Object));
            });
        });
    });
});
