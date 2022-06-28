/**
 * Returns results that have the value in the field array.
 */
const _ = require('underscore');

define(() => {
  'use strict';

  const ArrayFieldFilter = (field, value) => {
    this.field = field;
    this.value = value;
  };

  ArrayFieldFilter.prototype.filter = collection => collection.filter(
    _.bind(item => _.contains(item.get(this.field), this.value), this),
  );

  return ArrayFieldFilter;
});
