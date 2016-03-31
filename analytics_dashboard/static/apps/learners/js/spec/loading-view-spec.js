define([
    'backbone',
    'learners/js/views/loading-view',
    'underscore'
], function (Backbone, LoadingView, _) {
    'use strict';

    describe('LoadingView', function () {

        var fixtureClass = '.loading-fixture';

        beforeEach(function () {
            setFixtures('<div class="' + fixtureClass.slice(1) + '"></div>');
        });

        it('shows and hides loading template', function () {
            var loadingView = new LoadingView({
                model: new Backbone.Model(),
                el: fixtureClass,
                template: _.template('<div class="loading"><%= loadingText %></div>'),
                successView: new Backbone.View()
            });

            loadingView.render().onBeforeShow();
            expect(loadingView.$('.loading')).toContainText('Loading...');
            loadingView.model.trigger('sync');
            expect(loadingView.$('.loading')).not.toContainText('Loading...');
        });

    });
});
