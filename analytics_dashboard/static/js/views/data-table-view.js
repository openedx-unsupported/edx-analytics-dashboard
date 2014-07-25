define(['jquery', 'views/simple-model-attribute-view', 'underscore', 'dataTablesBootstrap'],
    function ($, SimpleModelAttributeView, _) {
        'use strict';

        var DataTableView = SimpleModelAttributeView.extend({

            initialize: function (options) {
                SimpleModelAttributeView.prototype.initialize.call(this, options);

                this.data = options.data;
                this.columns = options.columns;
                this.sorting = options.sorting || [];
            },

            _buildColumns: function ($row, dtColumns) {
                _.each(this.columns, function (column) {
                    $row.append('<th>' + column.title + '</th>');
                    dtColumns.push({data: column.key});
                });
            },

            _buildSorting: function () {
                var dtSorting = [];
                var sortRegexp = /^(-?)(.*)/g;
                var columns = _.map(this.columns, function (column) {
                    return column.key;
                });

                _.each(this.sorting, function (sorting) {
                    var match = sortRegexp.exec(sorting),
                        direction = match[1] === '-' ? 'desc' : 'asc',
                        index = columns.indexOf(match[2]);
                    dtSorting.push([index, direction]);
                });

                return dtSorting;
            },
            render: function () {
                var $parent = $('<div/>', {class:'table-responsive'}).appendTo(this.$el);
                var $table = $('<table/>', {class: 'table table-striped'}).appendTo($parent);
                var $thead = $('<thead/>').appendTo($table);
                var $row = $('<tr/>').appendTo($thead);
                var dtColumns = [];
                var dtConfig, dtSorting;

                this._buildColumns($row, dtColumns);

                dtConfig = {
                        paging: false,
                        info: false,
                        filter: false,
                        data: this.model.get(this.modelAttribute),
                        columns: dtColumns
                    };

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
