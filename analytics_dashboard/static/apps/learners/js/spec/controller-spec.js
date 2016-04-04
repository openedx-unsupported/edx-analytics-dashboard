define([
    'jquery',
    'learners/js/collections/learner-collection',
    'learners/js/controller',
    'learners/js/models/course-metadata',
    'learners/js/views/root-view'
], function ($, LearnerCollection, LearnersController, CourseMetadataModel, LearnersRootView) {
    'use strict';

    describe('LearnersController', function () {
        var courseId,
            server;

        courseId = 'test/course/id';

        beforeEach(function () {
            var collection;
            server = sinon.fakeServer.create();
            setFixtures('<div class="root-view"><div class="main"></div></div>');
            this.rootView = new LearnersRootView({el: '.root-view'});
            this.rootView.render();
            // The learner roster view looks at the first learner in
            // the collection in order to render a last updated
            // message.
            collection = new LearnerCollection([
                {
                    name: 'learner',
                    username: 'learner',
                    email: 'learner@example.com',
                    account_url: 'example.com/learner',
                    enrollment_mode: 'audit',
                    enrollment_date: new Date(),
                    cohort: null,
                    segments: ['highly_engaged'],
                    engagements: {},
                    last_updated: new Date(),
                    course_id: courseId
                }
            ]);
            this.controller = new LearnersController({
                rootView: this.rootView,
                learnerCollection: collection,
                courseMetadata: new CourseMetadataModel(),
                learnerEngagementTimelineUrl: '/test-endpoint/',
                courseId: courseId
            });
        });

        afterEach(function () {
            server.restore();
        });

        it('should show the learner roster page', function () {
            this.controller.showLearnerRosterPage();
            expect(this.rootView.$('.learner-roster')).toBeInDOM();
        });

        describe('navigating to the Learner Detail page', function () {
            it('should show the learner detail page', function () {
                var engagementTimelineResponse;
                this.controller.showLearnerDetailPage('example-username');
                // Showing the learner detail page triggers a request for the
                // learner engagement timeline data.
                engagementTimelineResponse = JSON.stringify({days: [{
                    date: '2016-01-01',
                    discussions_contributed: 1,
                    problems_attempted: 1,
                    problems_completed: 1,
                    videos_viewed: 1
                }]});
                server.requests[server.requests.length - 1].respond(200, {}, engagementTimelineResponse);
                expect(this.rootView.$('.learner-detail-container')).toExist();
            });

            it('should handle AJAX errors', function (done) {
                var rootView = this.rootView;
                this.controller.showLearnerDetailPage('example-username')
                    .always(function () {
                        expect(rootView.$('.learner-detail-container')).toExist();
                        expect(rootView.$('[role="alert"]')).toExist();
                        done();
                    });
                server.requests[server.requests.length - 1].respond(500, {}, '');
            });
        });

        it('should show the not found page', function () {
            this.controller.showNotFoundPage();
            expect(this.rootView.$el.html()).toContainText('Sorry, we couldn\'t find the page you\'re looking for.');
        });
    });
});
