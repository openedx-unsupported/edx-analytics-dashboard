/**
 * Returns results that match the field and value.
 */
define(() => {
  'use strict';

  class FieldFilter {
    constructor(field, value) {
      this.field = field;
      this.value = value;
    }

    filter(collection) {
      const filterOptions = {};
      filterOptions[this.field] = this.value;
      return collection.where(filterOptions);
    }
  }

  return FieldFilter;
});
