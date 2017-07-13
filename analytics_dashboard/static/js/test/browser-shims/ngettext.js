module.exports = function(singularString, pluralString, count) {
    'use strict';

    if (count === 1) {
        return singularString;
    } else {
        return pluralString;
    }
};
