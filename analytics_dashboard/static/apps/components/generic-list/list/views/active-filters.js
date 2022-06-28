define((require) => {
  'use strict';

  const $ = require('jquery');
  const _ = require('underscore');
  const ParentView = require('components/generic-list/common/views/parent-view');
  const NumResultsView = require('components/generic-list/list/views/num-results');

  const activeFiltersTemplate = require('components/generic-list/list/templates/active-filters.underscore');

  const ActiveFiltersView = ParentView.extend({
    events: {
      'click .action-clear-filter': 'clearOneFilter',
      'click .action-clear-all-filters': 'clearAllFilters',
    },

    regions: {
      numResultsSR: '.num-results-sr',
    },

    template: _.template(activeFiltersTemplate),

    initialize(options) {
      this.options = options || {};
      if (this.options.collection.mode === 'client') {
        this.listenTo(this.options.collection, 'backgrid:refresh', this.render);
      } else {
        this.listenTo(this.options.collection, 'sync', this.render);
      }

      // We need a second NumResultsView underneath active filters because both the number of results text and
      // the active filters need to be under the same aria-live region. This is because they are almost always
      // changed together and screen reader behavior of two aria-live regions updating at the same time is not
      // well-defined. This NumResultsView is placed within a hidden div so it is only read to screen readers.
      this.childViews = [
        {
          region: 'numResultsSR',
          class: NumResultsView,
          options: {
            collection: this.options.collection,
          },
        },
      ];
    },

    getFormattedActiveFilters(activeFilters) {
      const formattedFilters = [];
      const { collection } = this.options;

      _(activeFilters).each(function (filterVal, filterKey) {
        // create individual filters for each filter value (split by ','),
        // except for the text search where the user might enter in a comma
        const filterValues = filterKey === 'text_search'
          ? [filterVal] : filterVal.split(',');
        _(filterValues).each((filter) => {
          const formattedFilterVal = (filterKey === 'text_search')
            ? `"${filter}"` : collection.getFilterValueDisplayName(filterKey, filter);
          const filterDisplayName = collection.filterDisplayName(filterKey);
          // Translators: this is a label describing a filter selection that the user initiated.
          const displayName = _.template(gettext('<%= filterDisplayName %>: <%= filterVal %>'))({
            filterDisplayName,
            filterVal: formattedFilterVal,
          });
          formattedFilters.push({
            name: filter,
            filterKey,
            displayName: filterDisplayName === '' ? formattedFilterVal : displayName,
          });
        }, this);
      }, this);

      return formattedFilters;
    },

    templateHelpers() {
      // Note that search is included in 'activeFilters'
      let activeFilters = this.options.collection.getActiveFilterFields(true);
      const hasActiveFilters = !_.isEmpty(activeFilters);

      activeFilters = this.getFormattedActiveFilters(activeFilters);

      return {
        hasActiveFilters,
        activeFilters,
        activeFiltersTitle: gettext('Filters In Use:'),
        removeFilterMessage: gettext('Click to remove this filter'),
        // Translators: "Clear" in this context means "remove all of the filters"
        clearFiltersMessage: gettext('Clear'),
        clearFiltersSrMessage: gettext('Click to remove all filters'),
      };
    },

    clearOneFilter(event) {
      event.preventDefault();
      this.options.collection.clearFilter(
        $(event.currentTarget).data('filter-key'),
        $(event.currentTarget).data('filter-name'),
      );
    },

    clearAllFilters(event) {
      event.preventDefault();
      this.options.collection.clearAllFilters();
    },

    render() {
      ParentView.prototype.render.call(this);
      if (this.options.showChildrenOnRender) {
        this.showChildren();
      }
    },
  });

  return ActiveFiltersView;
});
