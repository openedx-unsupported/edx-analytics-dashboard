module.exports = (singularString, pluralString, count) => {
  'use strict';

  if (count === 1) {
    return singularString;
  }
  return pluralString;
};
