/**
 * Extends the filter view for drop down filters.
 */
define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),

        filterTemplate = require('text!components/filter/templates/drop-down-filter.underscore'),
        Filter = require('components/filter/views/filter');

    return Filter.extend({

        template: _.template(filterTemplate),

        /**
         * Returns the default template options along with an "All" option and the
         * current selection state.
         */
        templateHelpers: function() {
            var templateOptions = Filter.prototype.templateHelpers.call(this),
                filterValues = templateOptions.filterValues,
                selectedFilterValue;

            // update filter values with an "All" option and current selection
            if (filterValues.length > 0) {
                filterValues.unshift({
                    name: this.catchAllFilterValue,
                    // Translators: "All" refers to viewing all items (e.g. all courses).
                    displayName: gettext('All')
                });

                // Assumes that you can only filter by one filterKey at a time.
                selectedFilterValue = _.chain(filterValues)
                    .pluck('name')
                    .intersection(this.options.collection.getActiveFilterFields())
                    .first()
                    .value() || this.catchAllFilterValue;
                _.findWhere(filterValues, {name: selectedFilterValue}).selected = true;
            }

            return templateOptions;
        },

        onFilter: function(event) {
            var selectedOption = $(event.currentTarget).find('option:selected'),
                selectedFilterValue = selectedOption.val(),
                filterWasUnset = selectedFilterValue === this.catchAllFilterValue;
            event.preventDefault();
            if (filterWasUnset) {
                this.collection.unsetFilterField(this.options.filterKey);
            } else {
                this.collection.setFilterField(this.options.filterKey, selectedFilterValue);
            }

            this.filterUpdated(this.options.filterKey);
        }

    });
});
