define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        Marionette = require('marionette'),

        ActiveFiltersView,

        activeFiltersTemplate = require('text!components/generic-list/list/templates/active-filters.underscore');

    ActiveFiltersView = Marionette.ItemView.extend({
        events: {
            'click .action-clear-filter': 'clearOneFilter',
            'click .action-clear-all-filters': 'clearAllFilters'
        },

        template: _.template(activeFiltersTemplate),

        initialize: function(options) {
            this.options = options || {};
            this.listenTo(this.options.collection, 'sync', this.render);
        },

        getFormattedActiveFilters: function(activeFilters) {
            return _.mapObject(activeFilters, function(filterVal, filterKey) {
                var formattedFilterVal = (filterKey === 'text_search') ?
                    '"' + filterVal + '"' : filterVal.charAt(0).toUpperCase() + filterVal.slice(1),
                    filterDisplayName = this.options.collection.filterDisplayName(filterKey);
                return {
                    displayName: filterDisplayName + ': ' + formattedFilterVal
                };
            });
        },

        templateHelpers: function() {
            // Note that search is included in 'activeFilters'
            var activeFilters = this.options.collection.getActiveFilterFields(true),
                hasActiveFilters = !_.isEmpty(activeFilters);

            activeFilters = this.getFormattedActiveFilters(activeFilters);

            return {
                hasActiveFilters: hasActiveFilters,
                activeFilters: activeFilters,
                activeFiltersTitle: gettext('Filters In Use:'),
                removeFilterMessage: gettext('Click to remove this filter'),
                // Translators: "Clear" in this context means "remove all of the filters"
                clearFiltersMessage: gettext('Clear'),
                clearFiltersSrMessage: gettext('Click to remove all filters')
            };
        },

        clearOneFilter: function(event) {
            var filterKey;
            event.preventDefault();
            filterKey = $(event.currentTarget).data('filter-key');
            this.options.collection.unsetFilterField(filterKey);
            this.options.collection.refresh();
        },

        clearAllFilters: function(event) {
            event.preventDefault();
            this.options.collection.unsetAllFilterFields();
            this.options.collection.refresh();
        }
    });

    return ActiveFiltersView;
});
