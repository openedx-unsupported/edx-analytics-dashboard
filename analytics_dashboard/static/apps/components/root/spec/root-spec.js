define(function(require) {
    'use strict';

    var Backbone = require('backbone'),
        Marionette = require('marionette'),
        RootView = require('components/root/views/root'),
        PageModel = require('components/generic-list/common/models/page');

    describe('RootView', function() {
        beforeEach(function() {
            setFixtures('<div class=root-view-container></div>');
            this.rootView = new RootView({
                el: '.root-view-container',
                pageModel: new PageModel({
                    title: 'Testing Title',
                    lastUpdated: new Date(2016, 1, 28)
                }),
                appClass: 'test'
            }).render();
        });

        it('renders a main region', function() {
            this.rootView.showChildView('main', new (Backbone.View.extend({
                render: function() {
                    this.$el.html('example view');
                }
            }))());
            expect(this.rootView.$('.test-main-region').html()).toContainText('example view');
        });

        it('renders a header title and date', function() {
            expect(this.rootView.$('.test-header-region').html()).toContainText('Testing Title');
            expect(this.rootView.$('.test-header-region').html()).not.toContainText('February 28, 2016');
        });

        it('renders and clears alerts', function() {
            var childView = new Marionette.View();
            this.rootView.showChildView('main', childView);
            childView.triggerMethod('appError', {title: 'This is the error copy'});
            expect(this.rootView.$('.test-alert-region')).toHaveText('This is the error copy');
            this.rootView.triggerMethod('clearError', 'This is the error copy');
            expect(this.rootView.$('.test-alert-region')).not.toHaveText('This is the error copy');
        });
    });
});
