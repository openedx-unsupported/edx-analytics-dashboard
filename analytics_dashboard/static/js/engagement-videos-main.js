/**
 * Called for displaying a collection of video charts and tables.  Each bar represents a single video.
 */
require(['vendor/domReady!', 'load/init-page'], function(doc, page) {
    'use strict';

    require(['d3', 'underscore', 'views/data-table-view', 'views/stacked-bar-view'],
        function(d3, _, DataTableView, StackedBarView) {
            var model = page.models.courseModel,
                graphVideoColumns = [
                    {
                        key: 'users_at_end',
                        percent_key: 'end_percent',
                        title: gettext('Complete Views'),
                        className: 'text-right',
                        type: 'number',
                        color: '#58BC4B'
                    },
                    {
                        key: 'start_only_users',
                        percent_key: 'start_only_percent',
                        title: gettext('Incomplete Views'),
                        className: 'text-right',
                        type: 'number',
                        color: '#9B9B9B'
                    }
                ],
                tableColumns = [
                    {key: 'index', title: gettext('Order'), type: 'number', className: 'text-right'},
                    {key: 'name', title: model.get('contentTableHeading'), type: 'hasNull'}
                ],
                videoChart,
                videoTable;

            tableColumns = tableColumns.concat(graphVideoColumns);
            tableColumns.push({
                key: 'end_percent',
                title: gettext('Completion Percentage'),
                className: 'text-right',
                type: 'percent'
            });

            if (model.get('hasData')) {
                videoChart = new StackedBarView({
                    el: '#chart-view',
                    model: model,
                    modelAttribute: 'primaryContent',
                    trends: graphVideoColumns
                });
                videoChart.renderIfDataAvailable();
            }

            videoTable = new DataTableView({
                el: '[data-role=data-table]',
                model: model,
                modelAttribute: 'primaryContent',
                columns: tableColumns,
                sorting: ['index'],
                replaceZero: '-'
            });
            videoTable.renderIfDataAvailable();
        });
});
