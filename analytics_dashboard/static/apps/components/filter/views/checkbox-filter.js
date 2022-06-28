/**
 * Extends the filter view for checkbox filters.
 */
define((require) => {
  'use strict';

  const $ = require('jquery');
  const _ = require('underscore');

  const filterTemplate = require('components/filter/templates/checkbox-filter.underscore');
  const Filter = require('components/filter/views/filter');

  return Filter.extend({

    template: _.template(filterTemplate),

    /**
         * Returns the default template options along with the checkbox state.
         */
    templateHelpers() {
      const { collection } = this.options;
      const templateOptions = Filter.prototype.templateHelpers.call(this);

      _(templateOptions.filterValues).each(function (templateOption) {
        const filterValues = collection.getFilterFieldValue(this.options.filterKey);
        _(templateOption).extend({
          isChecked: !_(filterValues).isNull() && filterValues.indexOf(templateOption.name) > -1,
        });
      }, this);

      return templateOptions;
    },

    onFilter(event) {
      const $inputs = $(event.currentTarget).find('input:checkbox:checked');
      const filterKey = $(event.currentTarget).attr('id').slice(7); // chop off "filter-" prefix
      const appliedFilters = [];
      let filterValue = '';
      if ($inputs.length) {
        _.each($inputs, _.bind((input) => {
          appliedFilters.push($(input).attr('id'));
        }, this));
        filterValue = appliedFilters.join(',');
        this.collection.setFilterField(filterKey, filterValue);
      } else {
        this.collection.unsetFilterField(filterKey);
      }

      this.filterUpdated(filterValue);
    },

  });
});
