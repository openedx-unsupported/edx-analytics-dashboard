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

            _buildColumns: function ($row) {
                var self = this,
                    columns = [];
                _.each(self.options.columns, function (column) {
                    var columnOptions = {data: column.key};
                    $row.append('<th>' + column.title + '</th>');
                    _(['className', 'type']).each(function(option){
                        if(_(column).has(option)) {
                            columnOptions[option] = column[option];
                        }
                    });
                    columns.push(columnOptions);
                });
                return columns;
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
             * desirable for rendering dates.
             */
            _buildColumnDefs: function() {
                var self = this,
                    defs = [],
                    iColumn = 0;
                _(self.options.columns).each(function(column){
                    // currently, we only alter rendering of columns with type 'date'
                    if (column.type === 'date') {
                        defs.push({
                            render: function(data, type, row) {
                                // long month name, day, full year
                                return Utils.formatDate(data);
                            },
                            targets: iColumn
                        });
                        iColumn++;
                    }
                });
                return defs;
            },

            render: function () {
                AttributeListenerView.prototype.render.call(this);
                var self = this,
                    $parent = $('<div/>', {class:'table-responsive'}).appendTo(self.$el),
                    $table = $('<table/>', {class: 'table table-striped'}).appendTo($parent),
                    $thead = $('<thead/>').appendTo($table),
                    $row = $('<tr/>').appendTo($thead),
                    dtConfig,
                    dtSorting;

                dtConfig = {
                    paging: true,
                    info: false,
                    filter: false,
                    data: self.model.get(self.options.modelAttribute),
                    columns: self._buildColumns($row),
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
