/**
 * Displays a table of courses and a pagination control.
 */
define((require) => {
  'use strict';

  const $ = require('jquery');
  const _ = require('underscore');
  const Backgrid = require('backgrid');
  const ListTableView = require('components/generic-list/list/views/table');

  const CourseListBaseHeaderCell = require('course-list/list/views/base-header-cell');
  const CourseIdAndNameCell = require('course-list/list/views/course-id-and-name-cell');
  const courseListTableTemplate = require('course-list/list/templates/table.underscore');
  const notAvailableTemplate = require('course-list/list/templates/table-data-not-available.underscore');
  const Utils = require('utils/utils');

  const INTEGER_COLUMNS = ['count', 'cumulative_count', 'count_change_7_days', 'verified_enrollment', 'passing_users'];
  const DATE_COLUMNS = ['start_date', 'end_date'];

  // This attached to Backgrid.Extensions.MomentCell
  require('backgrid-moment-cell');

  const CourseListTableView = ListTableView.extend({
    template: _.template(courseListTableTemplate),
    regions: {
      table: '.course-list-table',
      paginator: '.course-list-paging-footer',
    },
    buildColumns() {
      return _.map(this.options.collection.sortableFields, (val, key) => {
        const column = this.createDefaultColumn(val.displayName, key);
        column.headerCell = CourseListBaseHeaderCell;
        if (INTEGER_COLUMNS.indexOf(key) !== -1) {
          column.cell = 'integer';
          column.sortValue = key; // reset to normal sorting for integer columns
        } else if (DATE_COLUMNS.indexOf(key) !== -1) {
          column.cell = Backgrid.Extension.MomentCell.extend({
            displayLang: Utils.getMomentLocale(),
            displayFormat: 'L',
            render() {
              const result = Backgrid.Extension.MomentCell.prototype.render.call(this, arguments);
              // Null values are rendered by MomentCell as "Invalid date". Convert to a nicer string:
              if (result.el.textContent === 'Invalid date') {
                // render the nicer text and screen reader only text
                $(result.el).html(_.template(notAvailableTemplate)({
                  srText: gettext('Date not available'),
                }));
              }
              return result;
            },
          });
        } else if (key === 'catalog_course_title') {
          column.cell = CourseIdAndNameCell;
        } else {
          column.cell = 'string';
        }

        return column;
      }, this);
    },
  });

  return CourseListTableView;
});
