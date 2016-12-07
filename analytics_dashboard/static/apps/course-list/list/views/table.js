/**
 * Displays a table of courses and a pagination control.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backgrid = require('backgrid'),
        Marionette = require('marionette'),

        BaseHeaderCell = require('course-list/list/views/base-header-cell'),
        CourseIdAndNameCell = require('course-list/list/views/course-id-and-name-cell'),
        PacingCell = require('course-list/list/views/pacing-cell'),
        PagingFooter = require('course-list/list/views/paging-footer'),
        courseListTableTemplate = require('text!course-list/list/templates/table.underscore'),
        Utils = require('utils/utils'),

        INTEGER_COLUMNS = ['count', 'cumulative_count', 'count_change_7_days', 'verified_enrollment'],
        DATE_COLUMNS = ['start_date', 'end_date'],
        CourseListTableView;

    // This attached to Backgrid.Extensions.MomentCell
    require('backgrid-moment-cell');

    CourseListTableView = Marionette.LayoutView.extend({
        template: _.template(courseListTableTemplate),
        regions: {
            table: '.course-list-table',
            paginator: '.course-list-paging-footer'
        },
        initialize: function(options) {
            this.options = options || {};
            this.collection.on('backgrid:sort', this.onSort, this);
        },
        onSort: function(column, direction) {
            this.options.trackingModel.trigger('segment:track', 'edx.bi.course_list.sorted', {
                category: column.get('name') + '_' + direction.slice(0, -6)
            });
        },
        onBeforeShow: function() {
            this.showChildView('table', new Backgrid.Grid({
                className: 'table table-striped dataTable',  // Combine bootstrap and datatables styling
                collection: this.options.collection,
                columns: _.map(this.options.collection.sortableFields, function(val, key) {
                    var column = {
                        label: val.displayName,
                        name: key,
                        editable: false,
                        sortable: true,
                        sortType: 'toggle',
                        headerCell: BaseHeaderCell
                    };
                    if (INTEGER_COLUMNS.indexOf(key) !== -1) {
                        column.cell = 'integer';
                    } else if (DATE_COLUMNS.indexOf(key) !== -1) {
                        column.cell = Backgrid.Extension.MomentCell.extend({
                            displayLang: Utils.getMomentLocale(),
                            displayFormat: 'L',
                            render: function() {
                                var result = Backgrid.Extension.MomentCell.prototype.render.call(this, arguments);
                                if (result.el.textContent === 'Invalid date') {
                                    result.el.textContent = '--';
                                }
                                return result;
                            }
                        });
                    } else if (key === 'catalog_course_title') {
                        column.cell = CourseIdAndNameCell;
                    } else if (key === 'pacing_type') {
                        column.cell = PacingCell;
                    } else {
                        column.cell = 'string';
                    }

                    return column;
                })
            }));
            this.showChildView('paginator', new PagingFooter({
                collection: this.options.collection,
                trackingModel: this.options.trackingModel
            }));
            // Accessibility hacks
            this.$('table').prepend('<caption class="sr-only">' + gettext('Course List') + '</caption>');
        }
    });

    return CourseListTableView;
});
