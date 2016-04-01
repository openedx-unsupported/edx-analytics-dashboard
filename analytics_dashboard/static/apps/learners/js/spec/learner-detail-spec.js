define([
    'learners/js/models/engagement-timeline',
    'learners/js/views/learner-detail'
], function (
    EngagementTimelineModel,
    LearnerDetailView
) {
    'use strict';

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

        it('renders a learner engagement timeline', function () {
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
    });
});
