define(function(require) {
    'use strict';

    var Backbone = require('backbone'),

        HeaderView = require('components/header/views/header');

    describe('HeaderView', function() {
        var fixture;

        beforeEach(function() {
            fixture = setFixtures('<div id="header-title"></div>');
        });

        it('renders updated title', function() {
            var pageModel = new Backbone.Model({title: 'First Title'});

            new HeaderView({
                el: '#header-title',
                model: pageModel
            }).render();

            expect(fixture).toContainText('First Title');
            expect(fixture).not.toContainText('Date Last Updated: unknown');
            pageModel.set('title', 'Updated Title');
            expect(fixture).toContainText('Updated Title');
        });

        it('renders a date', function() {
            var pageModel = new Backbone.Model({
                title: 'Initial Title',
                lastUpdated: new Date(2016, 0, 15)
            });

            new HeaderView({
                el: '#header-title',
                model: pageModel
            }).render();

            expect(fixture).not.toContainText('Date Last Updated: January 15, 2016');
        });
    });
});
