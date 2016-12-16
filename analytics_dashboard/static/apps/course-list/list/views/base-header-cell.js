define(function(require) {
    'use strict';

    var BaseHeaderCell = require('components/generic-list/list/views/base-header-cell'),

        CourseListBaseHeaderCell;

    CourseListBaseHeaderCell = BaseHeaderCell.extend({
        container: '.course-list-table'
    });

    return CourseListBaseHeaderCell;
});
