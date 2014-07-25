define(['jquery', 'backbone', 'dataTablesBootstrap', 'string'],
    function ($, Backbone) {
        'use strict';

        var DataTableView = Backbone.View.extend({

            initialize: function (options) {
                this.data = options.data;
                this.columns = options.columns;
                this.sorting = options.sorting || [];
            },

            _buildColumns: function ($row, dtColumns) {
                this.columns.forEach(function (column) {
                    $row.append('<th>' + column.capitalize() + '</th>');
                    dtColumns.push({data: column});
                });
            },

            _buildSorting: function () {
                var dtSorting = [];
                var sortRegexp = /^(-?)(.*)/g;
                var columns = this.columns;

                this.sorting.forEach(function (sorting) {
                    var match = sortRegexp.exec(sorting),
                        direction = match[1] === '-' ? 'desc' : 'asc',
                        index = columns.indexOf(match[2]);
                    dtSorting.push([index, direction]);
                });

                return dtSorting;
            },
            render: function () {
                var $table = $('<table/>', {class: 'table table-striped'}).appendTo(this.$el),
                    $thead = $('<thead/>').appendTo($table),
                    $row = $('<tr/>').appendTo($thead),
                    dtColumns = [];

                this._buildColumns($row, dtColumns);

                var dtConfig = {
                        paging: false,
                        info: false,
                        filter: false,
                        data: this.data,
                        columns: dtColumns
                    },
                    dtSorting = this._buildSorting();

                if (dtSorting.length) {
                    dtConfig.order = dtSorting;
                }

                $table.dataTable(dtConfig);

                return this;
            }

        });

        return DataTableView;
    }
);
