/**
/**
 * Extends the filter view for checkbox filters.
 */
define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),

        filterTemplate = require('text!components/filter/templates/checkbox-filter.underscore'),
        Filter = require('components/filter/views/filter');

    return Filter.extend({

        template: _.template(filterTemplate),

        /**
         * Returns the default template options along with the checkbox state.
         */
        templateHelpers: function() {
            var templateOptions = Filter.prototype.templateHelpers.call(this);
            if (this.options.filterKey in this.options.collection.getActiveFilterFields()) {
                templateOptions.isChecked = true;
            } else {
                templateOptions.isChecked = false;
            }
            return templateOptions;
        },

        onFilter: function(event) {
            var $inputs = $(event.currentTarget).find('input:checkbox:checked'),
                filterKey = $(event.currentTarget).attr('id').slice(7), // chop off "filter-" prefix
                appliedFilters = [],
                filterValue = '';
            if ($inputs.length) {
                _.each($inputs, _.bind(function(input) {
                    appliedFilters.push($(input).attr('id'));
                }, this));
                filterValue = appliedFilters.join(',');
                this.collection.setFilterField(filterKey, filterValue);
            } else {
                this.collection.unsetFilterField(filterKey);
            }

            this.filterUpdated(filterValue);
        }

    });
});
