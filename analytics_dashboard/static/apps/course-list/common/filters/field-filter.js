/**
 * Returns results that match the field and value.
 */
define(function() {
    'use strict';

    var FieldFilter;

    FieldFilter = function(field, value) {
        this.field = field;
        this.value = value;
    };

    FieldFilter.prototype.filter = function(collection) {
        var filterOptions = {};
        filterOptions[this.field] = this.value;
        return collection.where(filterOptions);
    };

    return FieldFilter;
});
