/**
 * Cell class which combines course id and name.  The name links
 * to the course home page.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),

        RowHeaderCell = require('components/generic-list/list/views/row-header-cell'),
        courseIdAndNameCellTemplate = require('text!course-list/list/templates/course-id-and-name-cell.underscore'),

        CourseIdAndNameCell;

    CourseIdAndNameCell = RowHeaderCell.extend({
        className: 'course-name-cell',
        template: _.template(courseIdAndNameCellTemplate),
        events: {
            click: 'emitTracking'
        },
        emitTracking: function() {
            this.$el.find('a').trigger('clicked.tracking');
        }
    });

    return CourseIdAndNameCell;
});
