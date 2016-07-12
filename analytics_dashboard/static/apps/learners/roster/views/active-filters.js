define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        Marionette = require('marionette'),

        LearnerCollection = require('learners/common/collections/learners'),

        ActiveFiltersView,

        activeFiltersTemplate = require('text!learners/roster/templates/active-filters.underscore');

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

        templateHelpers: function() {
            // Note that search is included in 'activeFilters'
            var activeFilters = this.options.collection.getActiveFilterFields(true),
                hasActiveFilters = !_.isEmpty(activeFilters);

            activeFilters = _.mapObject(activeFilters, function(filterVal, filterKey) {
                var filterDisplayName;
                if (filterKey === LearnerCollection.DefaultSearchKey) {
                    filterDisplayName = '"' + filterVal + '"';
                } else if (filterKey === 'cohort') {
                    // Translators: this is a label describing a selection that the user initiated.
                    filterDisplayName = _.template(gettext('Cohort: <%= filterVal %>'))({
                        filterVal: filterVal
                    });
                } else if (filterKey === 'enrollment_mode') {
                    // Translators: this is a label describing a selection that the user initiated.
                    filterDisplayName = _.template(gettext('Enrollment Track: <%= filterVal %>'))({
                        filterVal: filterVal
                    });
                } else {
                    filterDisplayName = filterVal;
                }
                return {
                    displayName: filterDisplayName
                };
            });

            return {
                hasActiveFilters: hasActiveFilters,
                activeFilters: activeFilters,
                activeFiltersTitle: gettext('Active Filters:'),
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
