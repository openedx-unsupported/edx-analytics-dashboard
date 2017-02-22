define(function(require) {
    'use strict';

    var _ = require('underscore'),
        ActiveFiltersView = require('components/generic-list/list/views/active-filters'),
        LearnerCollection = require('learners/common/collections/learners'),

        learnersActiveFiltersTemplate = require('text!learners/roster/templates/active-filters.underscore'),

        LearnersActiveFiltersView;

    LearnersActiveFiltersView = ActiveFiltersView.extend({
        template: _.template(learnersActiveFiltersTemplate),

        // This function is re-implemented from ActiveFiltersView because the filter display names here are
        // significantly different from the defaults.
        getFormattedActiveFilters: function(activeFilters) {
            return _.mapObject(activeFilters, function(filterVal, filterKey) {
                var formattedFilterVal = (filterKey === 'text_search') ?
                    filterVal : filterVal.charAt(0).toUpperCase() + filterVal.slice(1),
                    filterDisplayNames = {
                        // Translators: this is a label describing a selection that the user initiated.
                        cohort: _.template(gettext('Cohort: <%= filterVal %>'))({
                            filterVal: formattedFilterVal
                        }),
                        // Translators: this is a label describing a selection that the user initiated.
                        enrollment_mode: _.template(gettext('Enrollment Track: <%= filterVal %>'))({
                            filterVal: formattedFilterVal
                        }),
                        // Translators: this is a label describing a selection that the user initiated.
                        ignore_segments: _.template('<%= filterVal %>')({
                            filterVal: gettext('Active Learners')
                        })
                    },
                    filterDisplayName;
                filterDisplayNames[LearnerCollection.DefaultSearchKey] = '"' + formattedFilterVal + '"';
                if (filterKey in filterDisplayNames) {
                    filterDisplayName = filterDisplayNames[filterKey];
                }
                return {
                    name: filterVal,
                    filterKey: filterKey,
                    displayName: filterDisplayName.charAt(0).toUpperCase() + filterDisplayName.slice(1)
                };
            });
        }
    });

    return LearnersActiveFiltersView;
});
