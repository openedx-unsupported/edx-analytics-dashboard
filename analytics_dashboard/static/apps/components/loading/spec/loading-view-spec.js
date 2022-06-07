define((require) => {
  'use strict';

  const _ = require('underscore');
  const Backbone = require('backbone');

  const LoadingView = require('components/loading/views/loading-view');

  describe('LoadingView', () => {
    const fixtureClass = '.loading-fixture';

    beforeEach(() => {
      setFixtures(`<div class="${fixtureClass.slice(1)}"></div>`);
    });

    it('shows and hides loading template', () => {
      const loadingView = new LoadingView({
        model: new Backbone.Model(),
        el: fixtureClass,
        template: _.template('<div class="loading"><%= loadingText %></div>'),
        successView: new Backbone.View(),
      });

      loadingView.render().onBeforeShow();
      expect(loadingView.$('.loading')).toContainText('Loading...');
      loadingView.model.trigger('sync');
      expect(loadingView.$('.loading')).not.toContainText('Loading...');
    });
  });
});
