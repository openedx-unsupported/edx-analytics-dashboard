define(function(require) {
    'use strict';

    var BaseHeaderCell = require('generic-list/list/views/base-header-cell'),

        CourseListBaseHeaderCell;

    CourseListBaseHeaderCell = BaseHeaderCell.extend({
        container: '.course-list-table'
    });

    return CourseListBaseHeaderCell;
});
