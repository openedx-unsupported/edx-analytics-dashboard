define(['dataTablesBootstrap', 'jquery', 'underscore', 'utils/utils', 'views/attribute-listener-view'],
    function (dt, $, _, Utils, AttributeListenerView) {
        'use strict';

        var DataTableView = AttributeListenerView.extend({

            initialize: function (options) {
                AttributeListenerView.prototype.initialize.call(this, options);
                var self = this;

                self.options = options || {};
                self.options.sorting = options.sorting || [];

                self.renderIfDataAvailable();
            },

            _buildSorting: function () {
                var dtSorting = [];
                var sortRegexp = /^(-?)(.*)/g;
                var columns = _.map(this.options.columns, function (column) {
                    return column.key;
                });

                _.each(this.options.sorting, function (sorting) {
                    var match = sortRegexp.exec(sorting),
                        direction = match[1] === '-' ? 'desc' : 'asc',
                        index = columns.indexOf(match[2]);
                    dtSorting.push([index, direction]);
                });

                return dtSorting;
            },

            /**
             * Builds rendering for different cells in the table.  This is
             * desirable for rendering dates, percentages, etc. while keeping
             * the table sortable by the underlying data (rather than what's
             * necessarily displayed).
             */
            _buildColumnDefs: function () {
                var self = this,
                    defs = [],
                    iColumn = 0;
                _(self.options.columns).each(function (column) {
                    // default column definitions
                    var def = {
                        targets: iColumn,
                        data: function (row) {
                            // by default, display the value
                            return row[column.key];
                        },
                        // this text is displayed in the header
                        title: column.title,
                        className: column.className || undefined
                    };

                    // extend definitions to render different types of data
                    if (column.type === 'date') {
                        def.data = self.createFormatDateFunc(column.key);
                    } else if (column.type === 'percent') {
                        def.data = self.createFormatPercentFunc(column.key);
                    } else if (column.type ==='number') {
                        def.data = self.createFormatNumberFunc(column.key);
                    }

                    defs.push(def);
                    iColumn++;
                });
                return defs;
            },

            /**
             * Returns a function used by datatables to format the cell for
             * numbers.
             */
            createFormatNumberFunc: function (columnKey) {
                return function (row, type) {
                    var value = row[columnKey],
                        display = value;
                    if (type === 'display') {
                        display = Utils.localizeNumber(value);
                    }
                    return display;
                };
            },

            /**
             * Returns a function used by datatables to format the cell for
             * dates.
             */
            createFormatDateFunc: function (columnKey) {
                return function (row, type) {
                    var value = row[columnKey],
                        display = value;
                    if (type === 'display') {
                        // long month name, day, full year
                        display = Utils.formatDate(value);
                    }
                    return display;
                };
            },

            /**
             * Returns a function used by datatables to format the cell for
             * percentages.
             */
            createFormatPercentFunc: function (columnKey) {
                return function (row, type) {
                    var value = row[columnKey],
                        display = value;
                    if (type === 'display') {
                        display = ' ' + Utils.formatDisplayPercentage(value);
                    }
                    return display;
                };
            },

            render: function () {
                AttributeListenerView.prototype.render.call(this);
                var self = this,
                    $parent = $('<div/>', {class: 'table-responsive'}).appendTo(self.$el),
                    $table = $('<table/>', {class: 'table table-striped'}).appendTo($parent),
                    dtConfig,
                    dtSorting;

                dtConfig = {
                    paging: true,
                    info: false,
                    filter: false,
                    data: self.model.get(self.options.modelAttribute),
                    // providing 'columns' will override columnDefs
                    columnDefs: self._buildColumnDefs(),
                    // this positions the "length changing" control to the bottom
                    // using bootstrap styling
                    // more information at http://datatables.net/examples/basic_init/dom.html
                    dom: "<'row'<'col-xs-12't>><'row'<'col-xs-6'l><'col-xs-6'p>>"
                };

                dtSorting = self._buildSorting();

                if (dtSorting.length) {
                    dtConfig.order = dtSorting;
                }

                $table.dataTable(dtConfig);

                return self;
            }

        });

        return DataTableView;
    }
);
