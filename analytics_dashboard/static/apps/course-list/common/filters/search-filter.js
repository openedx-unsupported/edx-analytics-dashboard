/**
 * Wrapper around a regex matcher.  Returned results are those that match
 * the regex.
 */
define(() => {
  'use strict';

  let SearchFilter;

  SearchFilter = function (matcher) {
    this.matcher = matcher;
  };

  SearchFilter.prototype.filter = function (collection) {
    return collection.filter(this.matcher);
  };

  return SearchFilter;
});
