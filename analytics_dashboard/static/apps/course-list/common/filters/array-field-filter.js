/**
 * Returns results that have the value in the field array.
 */

define(() => {
  'use strict';

  const _ = require('underscore');

  const ArrayFieldFilter = (field, value) => {
    this.field = field;
    this.value = value;
  };

  ArrayFieldFilter.prototype.filter = collection => collection.filter(
    _.bind(item => _.contains(item.get(this.field), this.value), this),
  );

  return ArrayFieldFilter;
});
