define([
    'jquery',
    'learners/js/models/page-model',
    'learners/js/views/root-view',
    'marionette'
], function ($, PageModel, LearnersRootView, Marionette) {
    'use strict';

    describe('LearnersRootView', function () {
        beforeEach(function () {
            setFixtures('<div class=root-view-container></div>');
            this.rootView = new LearnersRootView({
                el: '.root-view-container',
                pageModel: new PageModel({
                    title: 'Testing Title',
                    lastUpdated: new Date(2016, 1, 28)
                })
            }).render();
        });

        it('renders a main region', function () {
            this.rootView.showChildView('main', new (Backbone.View.extend({
                render: function () {
                    this.$el.html('example view');
                }
            }))());
            expect(this.rootView.$('.learners-main-region').html()).toContainText('example view');
        });

        it('renders a header title and date', function () {
            expect(this.rootView.$('.learners-header-region').html()).toContainText('Testing Title');
            expect(this.rootView.$('.learners-header-region').html()).toContainText('February 28, 2016');
        });

        it('renders and clears errors', function () {
            var childView = new Marionette.View();
            this.rootView.showChildView('main', childView);
            childView.triggerMethod('appError', 'This is the error copy');
            expect(this.rootView.$('.learners-error-region')).toHaveText('This is the error copy');
            this.rootView.triggerMethod('clearError', 'This is the error copy');
            expect(this.rootView.$('.learners-error-region')).not.toHaveText('This is the error copy');
        });
    });
});
