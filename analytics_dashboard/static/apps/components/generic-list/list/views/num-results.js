define((require) => {
  'use strict';

  const _ = require('underscore');
  const Marionette = require('marionette');
  const Utils = require('utils/utils');

  const numResultsTemplate = require('components/generic-list/list/templates/num-results.underscore');

  const NumResultsView = Marionette.ItemView.extend({
    template: _.template(numResultsTemplate),

    initialize(options) {
      this.options = options || {};
      if (this.options.collection.mode === 'client') {
        this.listenTo(this.options.collection, 'backgrid:refresh', this.renderIfNotDestroyed);
      } else {
        this.listenTo(this.options.collection, 'sync', this.renderIfNotDestroyed);
      }
    },

    templateHelpers() {
      // Note that search is included in 'activeFilters'
      const numResults = this.options.collection.getResultCount();
      return {
        numResults: _.template(
          // Translators: 'count' refers to the number of results contained in the table.
          gettext('Number of results: <%= count %>'),
        )({
          count: Utils.localizeNumber(numResults, 0),
        }),
      };
    },

    renderIfNotDestroyed() {
      if (!this.isDestroyed) {
        this.render();
      }
    },
  });

  return NumResultsView;
});
