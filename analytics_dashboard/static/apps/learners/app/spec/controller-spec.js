define(function (require) {
    'use strict';

    var $ = require('jquery'),

        CourseMetadataModel = require('learners/common/models/course-metadata'),
        LearnerCollection = require('learners/common/collections/learners'),
        LearnersController = require('learners/app/controller'),
        LearnersRootView = require('learners/app/views/root'),
        PageModel = require('learners/common/models/page');

    describe('LearnersController', function () {
        var courseId,
            expectDetailPage,
            expectRosterPage,
            server;

        courseId = 'test/course/id';

        // convenience method for asserting that we are on the learner detail page
        expectDetailPage = function (rootView) {
            expect(rootView.$('.learner-detail-container')).toExist();
            expect(rootView.$('.learner-summary-container')).toExist();
            expect(rootView.$('.learners-header-region').html())
                .toContainText('Learner Details');
        };

        // convenience method for asserting that we are on the roster page
        expectRosterPage = function (rootView) {
            expect(rootView.$('.learner-roster')).toBeInDOM();
            expect(rootView.$('.learners-header-region').html()).toContainText('Learners');
        };

        beforeEach(function () {
            var collection,
                pageModel = new PageModel();

            server = sinon.fakeServer.create();
            setFixtures('<div class="root-view"><div class="main"></div></div>');
            this.rootView = new LearnersRootView({
                el: '.root-view',
                pageModel: pageModel
            });
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
                    last_updated: new Date(2016, 1, 28),
                    course_id: courseId
                }
            ], {parse: true});
            this.controller = new LearnersController({
                rootView: this.rootView,
                learnerCollection: collection,
                courseMetadata: new CourseMetadataModel(),
                pageModel: pageModel,
                learnerEngagementTimelineUrl: '/test-engagement-endpoint/',
                learnerListUrl: '/test-learner-endpoint/',
                courseId: courseId
            });
        });

        afterEach(function () {
            server.restore();
        });

        it('should show the learner roster page', function () {
            this.controller.showLearnerRosterPage();
            expectRosterPage(this.rootView);
        });

        describe('navigating to the Learner Detail page', function () {
            it('should show the learner detail page', function () {
                var engagementTimelineResponse;
                this.controller.showLearnerDetailPage('example-username');
                // Showing the learner detail page triggers a request for the
                // learner engagement timeline data.
                engagementTimelineResponse = JSON.stringify({days: [{
                    date: '2016-01-01',
                    discussion_contributions: 1,
                    problems_attempted: 1,
                    problems_completed: 1,
                    videos_viewed: 1
                }]});
                server.requests[server.requests.length - 1].respond(200, {}, engagementTimelineResponse);
                expectDetailPage(this.rootView);
            });

            it('should handle AJAX errors', function (done) {
                var view = this.controller.showLearnerDetailPage('example-username');

                view.once('appError', function (options) {
                    expect(options.title).toBe('Server error');
                    done();
                });

                server.requests[server.requests.length - 1].respond(500, {}, '');
            });
        });

        // The 'showPage' event gets fired by the router on the
        // controller any time a route is hit which should change the
        // current page.
        describe('showPage event', function () {
            it('renders the loading bar', function () {
                jasmine.clock().install();
                expect($('#nprogress')).not.toExist();
                this.controller.triggerMethod('showPage');
                expect($('#nprogress')).toExist();
                jasmine.clock().uninstall();
            });

            it('hides app-wide errors', function () {
                this.controller.showLearnerDetailPage('example-username');
                server.requests[server.requests.length - 1].respond(500, {});
                expectDetailPage(this.rootView);
                expect(this.rootView.$('[role="alert"]')).toExist();
                this.controller.triggerMethod('showPage');
                expect(this.rootView.$('[role="alert"]')).not.toExist();
            });
        });

        it('should show the not found page', function () {
            this.controller.showNotFoundPage();
            expect(this.rootView.$el.html()).toContainText("Sorry, we couldn't find the page you're looking for.");  // jshint ignore:line
        });
    });
});
