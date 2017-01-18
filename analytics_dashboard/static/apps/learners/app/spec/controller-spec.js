define(function(require) {
    'use strict';

    var $ = require('jquery'),

        CourseMetadataModel = require('learners/common/models/course-metadata'),
        LearnerCollection = require('learners/common/collections/learners'),
        LearnersController = require('learners/app/controller'),
        RootView = require('components/root/views/root'),
        PageModel = require('components/generic-list/common/models/page'),
        TrackingModel = require('models/tracking-model');

    describe('LearnersController', function() {
        var courseId,
            expectDetailPage,
            expectRosterPage,
            server;

        courseId = 'test/course/id';

        // convenience method for asserting that we are on the learner detail page
        expectDetailPage = function(controller) {
            var date = new Date(2016, 1, 28);
            expect(controller.options.rootView.$('.learners-navigation-region').html())
                .toContainText('Return to Learners');
            expect(controller.options.rootView.$('.learner-detail-container')).toExist();
            expect(controller.options.rootView.$('.learner-summary-container')).toExist();
            expect(controller.options.rootView.$('.learners-header-region').html())
                .toContainText('Learner Details');
            expect(controller.options.rootView.$('.learners-header-region').html())
                .not.toContainText(date.toLocaleDateString('en-us', {year: 'numeric', month: 'long', day: 'numeric'}));
        };

        // convenience method for asserting that we are on the roster page
        expectRosterPage = function(controller) {
            expect(controller.options.rootView.$('.learners-navigation-region').html())
                .not.toContainText('Return to Learners');
            expect(controller.options.rootView.$('.learner-roster')).toBeInDOM();
            expect(controller.options.rootView.$('.learners-header-region').html()).toContainText('Learners');
        };

        beforeEach(function() {
            var pageModel = new PageModel();

            server = sinon.fakeServer.create();
            setFixtures('<div class="root-view"><div class="main"></div></div>');
            this.rootView = new RootView({
                el: '.root-view',
                pageModel: pageModel,
                appClass: 'learners'
            });
            this.rootView.render();
            // The learner roster view looks at the first learner in
            // the collection in order to render a last updated
            // message.
            this.user = {
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
            };
            this.collection = new LearnerCollection([this.user], {parse: true, url: 'http://example.com'});
            this.controller = new LearnersController({
                rootView: this.rootView,
                learnerCollection: this.collection,
                courseMetadata: new CourseMetadataModel(),
                pageModel: pageModel,
                learnerEngagementTimelineUrl: '/test-engagement-endpoint/',
                learnerListUrl: '/test-learner-endpoint/',
                learnerListDownloadUrl: '/test-learner-endpoint.csv',
                courseId: courseId,
                trackingModel: new TrackingModel()
            });
        });

        afterEach(function() {
            server.restore();
        });

        it('should show the learner roster page', function() {
            this.controller.showLearnerRosterPage();
            expectRosterPage(this.controller);
        });

        it('should show the filtered learner roster page', function(done) {
            this.controller.showLearnerRosterPage('text_search=foo');
            expect(this.controller.options.learnerCollection.getSearchString()).toEqual('foo');
            this.controller.options.learnerCollection.once('sync', function() {
                expectRosterPage(this.controller);
                expect(this.controller.options.rootView.$('.learners-active-filters').html()).toContainText('foo');
                done();
            }, this, done);
            expect(this.controller.options.rootView.$('.learners-main-region').html()).toContainText('Loading...');
            server.requests[server.requests.length - 1].respond(200, {}, '{}');
        });

        it('should show invalid parameters alert with invalid URL parameters', function() {
            this.controller.showLearnerRosterPage('text_search=foo=');
            expect(this.controller.options.rootView.$('.learners-alert-region').html()).toContainText(
                'Invalid Parameters'
            );
            expect(this.controller.options.rootView.$('.learners-main-region').html()).toBe('');
        });

        describe('navigating to the Learner Detail page', function() {
            it('should show the learner detail page', function() {
                var engagementTimelineResponse;
                this.controller.showLearnerDetailPage('learner');
                // Showing the learner detail page triggers a request for the
                // learner engagement timeline data.
                engagementTimelineResponse = JSON.stringify({days: [{
                    date: '2016-01-01',
                    discussion_contributions: 1,
                    problems_attempted: 1,
                    problems_completed: 1,
                    videos_viewed: 1
                }]});
                server.requests[0].respond(200, {}, JSON.stringify(this.user));
                server.requests[server.requests.length - 1].respond(200, {}, engagementTimelineResponse);
                expectDetailPage(this.controller);
            });

            it('should handle AJAX errors', function(done) {
                var view = this.controller.showLearnerDetailPage('example-username');

                view.once('appError', function(options) {
                    expect(options.title).toBe('Server error');
                    done();
                });

                server.requests[server.requests.length - 1].respond(500, {}, '');
            });

            it('should have query string in return to learners navigation link', function() {
                this.collection.state.currentPage = 2;
                this.collection.setSearchString('foobar');
                this.controller.showLearnerDetailPage('learner');
                server.requests[0].respond(200, {}, JSON.stringify(this.user));
                server.requests[server.requests.length - 1].respond(200, {}, JSON.stringify({}));
                expect(this.controller.options.rootView.$('.learners-navigation-region a').attr('href'))
                    .toEqual('#?text_search=foobar&page=2');
            });
        });

        // The 'showPage' event gets fired by the router on the
        // controller any time a route is hit which should change the
        // current page.
        describe('showPage event', function() {
            it('renders the loading bar', function() {
                jasmine.clock().install();
                expect($('#nprogress')).not.toExist();
                this.controller.triggerMethod('showPage');
                expect($('#nprogress')).toExist();
                jasmine.clock().uninstall();
            });

            it('hides app-wide errors', function() {
                this.controller.showLearnerDetailPage('learner');
                server.requests[0].respond(200, {}, JSON.stringify(this.user));
                server.requests[server.requests.length - 1].respond(500, {});
                expectDetailPage(this.controller);
                expect(this.rootView.$('[role="alert"]')).toExist();
                this.controller.triggerMethod('showPage');
                expect(this.rootView.$('[role="alert"]')).not.toExist();
            });
        });

        it('should show the not found page', function() {
            this.controller.showNotFoundPage();
            // eslint-disable-next-line max-len
            expect(this.rootView.$el.html()).toContainText("Sorry, we couldn't find the page you're looking for.");
        });
    });
});
