/**
 * Displays a table of courses and a pagination control.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backgrid = require('backgrid'),
        Marionette = require('marionette'),

        BaseHeaderCell = require('course-list/list/views/base-header-cell'),
        PagingFooter = require('course-list/list/views/paging-footer'),
        courseListTableTemplate = require('text!course-list/list/templates/table.underscore'),

        INTEGER_COLUMNS = ['count', 'cumulative_count', 'count_change_7_days', 'verified_enrollment'],
        CourseListTableView;

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
            this.collection.flattenVerified();
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
                    if (key in INTEGER_COLUMNS) {
                        column.cell = 'integer';
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
