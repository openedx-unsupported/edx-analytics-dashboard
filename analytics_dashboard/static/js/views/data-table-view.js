define(['dataTablesBootstrap', 'jquery', 'underscore', 'views/simple-model-attribute-view'],
    function (dt, $, _, SimpleModelAttributeView) {
        'use strict';

        var DataTableView = SimpleModelAttributeView.extend({

            initialize: function (options) {
                SimpleModelAttributeView.prototype.initialize.call(this, options);
                var self = this;

                self.options = options || {};
                self.options.sorting = options.sorting || [];

                // go ahead and render if the data exists
                if(self.model.has(self.modelAttribute)) {
                    self.render();
                }
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
                var $parent = $('<div/>', {class:'table-responsive'}).appendTo(this.$el);
                var $table = $('<table/>', {class: 'table table-striped'}).appendTo($parent);
                var $thead = $('<thead/>').appendTo($table);
                var $row = $('<tr/>').appendTo($thead);
                var dtColumns = [];
                var dtConfig, dtSorting;

                dtColumns = this._buildColumns($row);

                dtConfig = {
                        paging: false,
                        info: false,
                        filter: false,
                        data: this.model.get(this.options.modelAttribute),
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
