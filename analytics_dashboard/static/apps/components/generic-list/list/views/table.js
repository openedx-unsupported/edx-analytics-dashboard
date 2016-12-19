/**
 * Displays a table of items and a pagination control.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backgrid = require('backgrid'),
        Marionette = require('marionette'),

        BaseHeaderCell = require('./base-header-cell'),
        PagingFooter = require('./paging-footer'),
        listTableTemplate = require('text!../templates/table.underscore'),

        ListTableView;

    ListTableView = Marionette.LayoutView.extend({
        template: _.template(listTableTemplate),
        regions: {
            table: '.list-table',
            paginator: '.list-paging-footer'
        },
        initialize: function(options) {
            this.options = options || {};
            this.collection.on('backgrid:sort', this.onSort, this);
            this.trackSortEventName = 'edx.bi.list.sorted';
            this.tableName = gettext('Generic List');
        },
        onSort: function(column, direction) {
            this.options.trackingModel.trigger('segment:track', this.trackSortEventName, {
                category: column.get('name') + '_' + direction.slice(0, -6)
            });
        },
        onBeforeShow: function() {
            this.showChildView('table', new Backgrid.Grid({
                className: 'table table-striped dataTable',  // Combine bootstrap and datatables styling
                collection: this.options.collection,
                columns: this.buildColumns()
            }));
            this.showChildView('paginator', new PagingFooter({
                collection: this.options.collection,
                trackingModel: this.options.trackingModel
            }));
            // Accessibility hacks
            this.$('table').prepend('<caption class="sr-only">' + this.tableName + '</caption>');
        },
        buildColumns: function() {
            return _.map(this.options.collection.sortableFields, function(val, key) {
                var column = {
                    label: val.displayName,
                    name: key,
                    editable: false,
                    sortable: true,
                    sortType: 'toggle',
                    headerCell: BaseHeaderCell,
                    cell: 'string'
                };

                return column;
            });
        }
    });

    return ListTableView;
});
