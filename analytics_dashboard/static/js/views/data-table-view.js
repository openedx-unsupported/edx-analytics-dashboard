define(['dataTablesBootstrap', 'jquery', 'underscore', 'views/attribute-listener-view'],
    function (dt, $, _, AttributeListenerView) {
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
                    $row.append('<th>' + column.title + '</th>');
                    columns.push({data: column.key});
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

            render: function () {
                AttributeListenerView.prototype.render.call(this);
                var self = this,
                    $parent = $('<div/>', {class:'table-responsive'}).appendTo(this.$el),
                    $table = $('<table/>', {class: 'table table-striped'}).appendTo($parent),
                    $thead = $('<thead/>').appendTo($table),
                    $row = $('<tr/>').appendTo($thead),
                    dtColumns,
                    dtConfig,
                    dtSorting;

                dtColumns = self._buildColumns($row);

                dtConfig = {
                        paging: false,
                        info: false,
                        filter: false,
                        data: this.model.get(self.options.modelAttribute),
                        columns: dtColumns
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
