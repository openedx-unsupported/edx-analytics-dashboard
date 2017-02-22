define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),
        Utils = require('utils/utils'),

        NumResultsView,

        numResultsTemplate = require('text!components/generic-list/list/templates/num-results.underscore');

    NumResultsView = Marionette.ItemView.extend({
        template: _.template(numResultsTemplate),

        initialize: function(options) {
            this.options = options || {};
            if (this.options.collection.mode === 'client') {
                this.listenTo(this.options.collection, 'backgrid:refresh', this.renderIfNotDestroyed);
            } else {
                this.listenTo(this.options.collection, 'sync', this.renderIfNotDestroyed);
            }
        },

        templateHelpers: function() {
            // Note that search is included in 'activeFilters'
            var numResults = this.options.collection.getResultCount();
            return {
                numResults: _.template(
                    // Translators: 'count' refers to the number of results contained in the table.
                    gettext('Number of results: <%= count %>')
                )({
                    count: Utils.localizeNumber(numResults, 0)
                })
            };
        },

        renderIfNotDestroyed: function() {
            if (this.isDestroyed) {
                return;
            } else {
                this.render();
            }
        }
    });

    return NumResultsView;
});
