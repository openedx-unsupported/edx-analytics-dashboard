require(['vendor/domReady!', 'load/init-page'], function (doc, page) {
    'use strict';

    require(['d3', 'underscore', 'views/data-table-view', 'views/stacked-bar-view'],
        function (d3, _, DataTableView, StackedBarView) {
            var model = page.models.courseModel,
                graphSubmissionColumns = [
                    {
                        key: 'average_correct_submissions',
                        percent_key: 'correct_percent',
                        title: gettext('Average Correct'),
                        className: 'text-right',
                        type: 'number',
                        fractionDigits: 1,
                        color: '#4BB4FB'
                    },
                    {
                        key: 'average_incorrect_submissions',
                        percent_key: 'incorrect_percent',
                        title: gettext('Average Incorrect'),
                        className: 'text-right',
                        type: 'number',
                        fractionDigits: 1,
                        color: '#CA0061'
                    }
                ],
                tableColumns = [
                    {key: 'index', title: gettext('Order'), type: 'number', className: 'text-right'},
                    {key: 'name', title: model.get('contentTableHeading'), type: 'hasNull'},
                    {key: 'num_modules', title: gettext('Problems'), type: 'number', className: 'text-right'}
                ];

            tableColumns = tableColumns.concat(graphSubmissionColumns);

            tableColumns.push({
                key: 'average_submissions',
                title: gettext('Average Submissions Per Problem'),
                className: 'text-right',
                type: 'number',
                fractionDigits: 1,
                color: '#4BB4FB'
            });

            tableColumns.push({
                key: 'correct_percent',
                title: gettext('Percentage Correct'),
                className: 'text-right',
                type: 'percent'
            });

            if (model.get('hasData')) {
                new StackedBarView({
                    el: '#chart-view',
                    model: model,
                    modelAttribute: 'primaryContent',
                    dataType: 'decimal',
                    trends: graphSubmissionColumns
                });
            }

            new DataTableView({
                el: '[data-role=data-table]',
                model: model,
                modelAttribute: 'primaryContent',
                columns: tableColumns,
                sorting: ['index'],
                replaceZero: '-'
            });
        });
});
