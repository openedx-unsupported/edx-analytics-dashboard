/**
 * Called for displaying aggregate video charts and tables.  Each bar is a collection of video views.
 */
require(['vendor/domReady', 'load/init-page'], function(doc, page) {
    'use strict';

    require(['d3', 'underscore', 'views/data-table-view', 'views/stacked-bar-view'],
        function(d3, _, DataTableView, StackedBarView) {
            var model = page.models.courseModel,
                graphVideoColumns = [
                    {
                        key: 'average_users_at_end',
                        percent_key: 'end_percent',
                        title: gettext('Average Complete Views'),
                        className: 'text-right',
                        type: 'number',
                        fractionDigits: 1,
                        color: '#58BC4B'
                    },
                    {
                        key: 'average_start_only_users',
                        percent_key: 'start_only_percent',
                        title: gettext('Average Incomplete Views'),
                        className: 'text-right',
                        type: 'number',
                        fractionDigits: 1,
                        color: '#9B9B9B'
                    }
                ],
                tableColumns = [
                    {key: 'index', title: gettext('Order'), type: 'number', className: 'text-right'},
                    {key: 'name', title: model.get('contentTableHeading'), type: 'hasNull'},
                    {key: 'num_modules', title: gettext('Videos'), type: 'number', className: 'text-right'}
                ],
                videoContentChart,
                videoContentTable;

            tableColumns = tableColumns.concat(graphVideoColumns);
            tableColumns.push({
                key: 'end_percent',
                title: gettext('Completion Percentage'),
                className: 'text-right',
                type: 'percent'
            });

            if (model.get('hasData')) {
                videoContentChart = new StackedBarView({
                    el: '#chart-view',
                    model: model,
                    modelAttribute: 'primaryContent',
                    dataType: 'decimal',
                    trends: graphVideoColumns
                });
                videoContentChart.renderIfDataAvailable();
            }

            videoContentTable = new DataTableView({
                el: '[data-role=data-table]',
                model: model,
                modelAttribute: 'primaryContent',
                columns: tableColumns,
                sorting: ['index'],
                replaceZero: '-'
            });
            videoContentTable.renderIfDataAvailable();
        });
});
