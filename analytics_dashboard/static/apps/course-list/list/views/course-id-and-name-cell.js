/**
 * Cell class which combines course id and name.  The name links
 * to the course home page.
 */
define((require) => {
  'use strict';

  const _ = require('underscore');

  const RowHeaderCell = require('components/generic-list/list/views/row-header-cell');
  const courseIdAndNameCellTemplate = require('course-list/list/templates/course-id-and-name-cell.underscore');

  const CourseIdAndNameCell = RowHeaderCell.extend({
    className: 'course-name-cell',
    template: _.template(courseIdAndNameCellTemplate),
    events: {
      click: 'emitTracking',
    },
    emitTracking() {
      this.$el.find('a').trigger('clicked.tracking');
    },
  });

  return CourseIdAndNameCell;
});
