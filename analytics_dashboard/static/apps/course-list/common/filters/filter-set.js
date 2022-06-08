/**
 * ANDs or ORs the results produced by the provided filters or filter sets.
 */
define((require) => {
  'use strict';

  const _ = require('underscore');

  class FilterSet {
    constructor(mode, filters) {
      const validModes = ['AND', 'OR'];
      if (!_(validModes).contains(mode)) {
        throw new Error(`Only valid modes are: ${validModes.join(', ')}`);
      }
      this.mode = mode;
      this.filters = filters;
    }

    /**
         * If no filters are provided, then all models are returned.  Otherwise,
         * the filters are ANDed or ORed.
         */
    filter(collection) {
      let models;
      if (this.filters.length === 0) {
        models = collection.models;
      } else {
        _(this.filters).each(filter => {
          const filteredModels = filter.filter(collection);
          if (_(models).isUndefined()) {
            models = filteredModels;
          } else if (this.mode === 'AND') {
            models = _(filteredModels).intersection(models);
          } else if (this.mode === 'OR') {
            models = _(filteredModels).union(models);
          }
        }, this);
      }
      return models;
    }
  }

  return FilterSet;
});
