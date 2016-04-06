define([
    'backbone',
    'learners/js/collections/learner-collection',
    'learners/js/views/header',
], function (Backbone, LearnerCollection, HeaderView) {
    'use strict';

    describe('HeaderView', function () {
        var fixture;

        beforeEach(function () {
            fixture = setFixtures('<div id="header-title"></div>');
        });

        it('renders updated title', function () {
            var pageModel = new Backbone.Model({title: 'First Title'});

            new HeaderView({
                el: '#header-title',
                model: pageModel
            }).render();

            expect(fixture).toContainText('First Title');
            expect(fixture).toContainText('Date Last Updated: unknown');
            pageModel.set('title', 'Updated Title');
            expect(fixture).toContainText('Updated Title');
        });

        it('renders a date', function () {
            var pageModel = new Backbone.Model({
                    title: 'Initial Title',
                    lastUpdated: new Date(2016, 0, 15)
                });

            new HeaderView({
                el: '#header-title',
                model: pageModel
            }).render();

            expect(fixture).toContainText('Date Last Updated: January 15, 2016');
        });

    });
});
