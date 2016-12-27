/**
 * Cell class which combines course id and name.  The name links
 * to the course home page.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backgrid = require('backgrid'),

        courseIdAndNameCellTemplate = require('text!course-list/list/templates/course-id-and-name-cell.underscore'),

        CourseIdAndNameCell;

    CourseIdAndNameCell = Backgrid.Cell.extend({
        className: 'course-name-cell',
        template: _.template(courseIdAndNameCellTemplate),
        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        }
    });

    return CourseIdAndNameCell;
});
