/**
 * Wrapper around a regex matcher.  Returned results are those that match
 * the regex.
 */
define(() => {
  'use strict';

  class SearchFilter {
    constructor(matcher) {
      this.matcher = matcher;
    }

    filter(collection) {
      return collection.filter(this.matcher);
    }
  }

  return SearchFilter;
});
