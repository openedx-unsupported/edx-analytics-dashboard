define([
    'jquery',
    'learners/js/collections/learner-collection',
    'learners/js/controller',
    'marionette'
], function ($, LearnerCollection, LearnersController, Marionette) {
    'use strict';

    describe('LearnersController', function () {
        beforeEach(function () {
            var collection;
            setFixtures('<div class="root-view"><div class="main"></div></div>');
            this.rootView = new (Marionette.LayoutView.extend({
                regions: {
                    main: '.main'
                }
            }))({el: '.root-view'});
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
                    course_id: 'test/course/id'
                }
            ]);
            this.controller = new LearnersController({rootView: this.rootView, learnerCollection: collection});
        });

        it('should show the learner roster page', function () {
            this.controller.showLearnerRosterPage();
            expect(this.rootView.$('.learner-roster')).toBeInDOM();
        });

        it('should show the learner detail page', function () {
            // The current learner detail page is a stub.  The actual
            // page will be implemented in
            // https://openedx.atlassian.net/browse/AN-6191
            this.controller.showLearnerDetailPage('example-username');
            expect(this.rootView.$el.html()).toContainText('example-username');
        });

        it('should show the not found page', function () {
            this.controller.showNotFoundPage();
            expect(this.rootView.$el.html()).toContainText('Sorry, we couldn\'t find the page you\'re looking for.');
        });
    });
});
