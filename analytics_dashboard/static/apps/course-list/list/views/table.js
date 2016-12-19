/**
 * Displays a table of courses and a pagination control.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backgrid = require('backgrid'),
        ListTableView = require('components/generic-list/list/views/table'),

        BaseHeaderCell = require('course-list/list/views/base-header-cell'),
        CourseIdAndNameCell = require('course-list/list/views/course-id-and-name-cell'),
        PacingCell = require('course-list/list/views/pacing-cell'),
        courseListTableTemplate = require('text!course-list/list/templates/table.underscore'),
        Utils = require('utils/utils'),

        INTEGER_COLUMNS = ['count', 'cumulative_count', 'count_change_7_days', 'verified_enrollment'],
        DATE_COLUMNS = ['start_date', 'end_date'],
        CourseListTableView;

    // This attached to Backgrid.Extensions.MomentCell
    require('backgrid-moment-cell');

    CourseListTableView = ListTableView.extend({
        template: _.template(courseListTableTemplate),
        regions: {
            table: '.course-list-table',
            paginator: '.course-list-paging-footer'
        },
        initialize: function(options) {
            ListTableView.prototype.initialize.call(this, options);
            this.trackSortEventName = 'edx.bi.course_list.sorted';
            this.trackPageEventName = 'edx.bi.course_list.paged';
            this.tableName = gettext('Course List');
            this.appClass = 'course-list';
        },
        buildColumns: function() {
            return _.map(this.options.collection.sortableFields, function(val, key) {
                var column = {
                    label: val.displayName,
                    name: key,
                    editable: false,
                    sortable: true,
                    sortType: 'toggle',
                    sortValue: function(model, colName) {
                        var sortVal = model.get(colName);
                        if (sortVal === null || sortVal === undefined || sortVal === '') {
                            // Force null values to the end of the ascending sorted list
                            // NOTE: only works for sorting string value columns
                            return 'z';
                        } else {
                            return 'a ' + sortVal;
                        }
                    },
                    headerCell: BaseHeaderCell
                };
                if (INTEGER_COLUMNS.indexOf(key) !== -1) {
                    column.cell = 'integer';
                    column.sortValue = key; // reset to normal sorting for integer columns
                } else if (DATE_COLUMNS.indexOf(key) !== -1) {
                    column.cell = Backgrid.Extension.MomentCell.extend({
                        displayLang: Utils.getMomentLocale(),
                        displayFormat: 'L',
                        render: function() {
                            var result = Backgrid.Extension.MomentCell.prototype.render.call(this, arguments);
                            // Null values are rendered by MomentCell as "Invalid date". Convert to a nicer string:
                            if (result.el.textContent === 'Invalid date') {
                                result.el.textContent = '--';
                                $(result.el).attr('aria-label', 'None defined');
                            }
                            return result;
                        }
                    });
                } else if (key === 'catalog_course_title') {
                    column.cell = CourseIdAndNameCell;
                } else if (key === 'pacing_type') {
                    // NOTE: pacing type is a filterable field now, which means it is not displayed as a column in the
                    // table. However, I'm keeping this here (along with the pacing-cell.js/underscore) in case we will
                    // ever want to display it again in the future. If we are sure that will never happen, then delete.
                    column.cell = PacingCell;
                } else {
                    column.cell = 'string';
                }

                return column;
            });
        }
    });

    return CourseListTableView;
});
