define(['dataTablesBootstrap', 'jquery', 'naturalSort', 'underscore', 'utils/utils', 'views/attribute-listener-view'],
    function (dt, $, naturalSort, _, Utils, AttributeListenerView) {
        'use strict';

        var DataTableView = AttributeListenerView.extend({

            initialize: function (options) {
                AttributeListenerView.prototype.initialize.call(this, options);
                var self = this;

                self.options = options || {};
                self.options.sorting = options.sorting || [];

                self.addNaturalSort();
                self.renderIfDataAvailable();
            },

            /**
             * Adds natural sort to the data table sorting.
             */
            addNaturalSort: function() {
                $.fn.dataTableExt.oSort['natural-asc'] = function (a, b) {
                    return naturalSort(a,b);
                };
                $.fn.dataTableExt.oSort['natural-desc'] = function (a, b) {
                    return -naturalSort(a,b);
                };
            },

            _buildSorting: function () {
                var self = this,
                    dtSorting = [],
                    sortRegexp = /^(-?)(.*)/g,
                    columns = _.map(self.options.columns, function (column) {
                        return column.key;
                    });

                _.each(self.options.sorting, function (sorting) {
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
                    } else if (column.type === 'number') {
                        def.data = self.createFormatNumberFunc(column.key, column.fractionDigits);
                    } else if (column.type === 'maxNumber') {
                        // this is useful so that sorting is number based, but
                        // '+' can be displayed after the maximum
                        def.data = self.createFormatMaxNumberFunc(column.key, column.maxNumber);
                        // this column has a mix of numbers and strings
                        def.type = 'natural';
                    } else if (column.type === 'bool') {
                        def.data = self.createFormatBoolFunc(column.key);
                    } else if (column.type === 'hasNull') {
                        def.data = self.createFormatHasNullFunc(column.key);
                    } else if (column.type === 'time') {
                        def.data = self.createFormatTimeFunc(column.key);
                    }

                    defs.push(def);
                    iColumn++;
                });
                return defs;
            },

            createFormatTimeFunc: function (columnKey) {
                return function (row, type) {
                    var value = row[columnKey],
                        display = value;
                    if (type === 'display') {
                        display = Utils.formatTime(Number(value));
                    }
                    return display;
                };
            },

            /**
             * Returns a function used by datatables to format the cell for
             * numbers.
             */
            createFormatNumberFunc: function (columnKey, fractionDigits) {
                var self = this;
                return function (row, type) {
                    var value = row[columnKey],
                        display = value;
                    if (type === 'display') {
                        if (_(self.options).has('replaceZero') && value === 0) {
                            display = self.options.replaceZero;
                        } else if (!_(value).isUndefined() && !_(value).isNull()){
                            display = Utils.localizeNumber(Number(value), fractionDigits);
                        }
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
             * to display a '+' after the maximum number.
             */
            createFormatMaxNumberFunc: function(columnKey, maxNumber) {
                return function(row, type) {
                    var value = row[columnKey],
                        display = value;
                    // isNaN() return true for strings -- e.g. 'Unknown'
                    if (type === 'display' && !isNaN(value)) {
                        display = Utils.localizeNumber(value);
                        if (value >= maxNumber) {
                            display = display + '+';
                        }
                    }
                    return display;
                };
            },

            /**
             * Returns a function used by datatables to format the cell for
             * percentages.
             */
            createFormatPercentFunc: function (columnKey) {
                var self = this;
                return function (row, type) {
                    var value = row[columnKey],
                        display = value;
                    if (type === 'display') {
                        if (_(self.options).has('replaceZero') && value === 0) {
                            display = self.options.replaceZero;
                        } else {
                            display = Utils.formatDisplayPercentage(value);
                        }
                    }
                    return display;
                };
            },

            /**
             * Returns a function used by datatables to display null values as
             * "(empty)".
             */
            createFormatHasNullFunc: function(columnKey) {
                return function (row, type) {
                    var value = row[columnKey],
                        display = value;
                    if (type === 'display' && _(display).isNull()) {
                        /**
                         * Translators: (empty) is displayed in a table and indicates no label/value.
                         * Keep text in the parenthesis or an equivalent symbol.
                         */
                        display = gettext('(empty)');
                    }
                    return display;
                };
            },

            /**
             * Returns a function used by datatables to format the cell for
             * booleans (Correct vs -).
             */
            createFormatBoolFunc: function (columnKey) {
                return function (row, type) {
                    var value = row[columnKey],
                        display = value;
                    if (type === 'display') {
                        if (value) {
                            // Translators: "Correct" is displayed in a table..
                            display = gettext('Correct');
                        } else {
                            display = '-';
                        }
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

                    // this positions the "length changing" control to the bottom using bootstrap styling
                    // more information at http://datatables.net/examples/basic_init/dom.html
                    dom: '<"row"<"col-xs-12"t>><"row"<"col-xs-6"l><"col-xs-6"p>>',

                    // Disable auto-width as it causes the date column to wrap unnecessarily.
                    autoWidth: false
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
