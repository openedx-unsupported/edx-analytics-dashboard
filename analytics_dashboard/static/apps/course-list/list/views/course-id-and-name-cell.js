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
        tagName: 'th',
        className: 'course-name-cell',
        template: _.template(courseIdAndNameCellTemplate),
        events: {
            click: 'emitTracking'
        },
        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
            this.$el.attr('scope', 'row');
            return this;
        },
        emitTracking: function() {
            this.$el.find('a').trigger('clicked.tracking');
        }
    });

    return CourseIdAndNameCell;
});
