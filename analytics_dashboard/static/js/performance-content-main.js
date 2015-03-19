require(['vendor/domReady!', 'load/init-page'], function (doc, page) {
    'use strict';

    require(['d3', 'underscore', 'views/data-table-view', 'views/stacked-bar-view'],
        function (d3, _, DataTableView, StackedBarView) {
            var model = page.models.courseModel,
                graphSubmissionColumns = [
                    {
                        key: 'correct_submissions',
                        percent_key: 'correct_percent',
                        title: gettext('Correct'),
                        className: 'text-right',
                        type: 'number',
                        color: '#4BB4FB'
                    },
                    {
                        key: 'incorrect_submissions',
                        percent_key: 'incorrect_percent',
                        title: gettext('Incorrect'),
                        className: 'text-right',
                        type: 'number',
                        color: '#CA0061'
                    }
                ],
                tableColumns = [
                    {key: 'index', title: gettext('Order'), type: 'number', className: 'text-right'},
                    {key: 'name', title: model.get('contentTableHeading'), type: 'hasNull'}
                ];

            if (model.get('showProblemCount')) {
                tableColumns.push({
                    key: 'num_children',
                    title: gettext('Problems'),
                    type: 'number', className: 'text-right'
                });
            }
            tableColumns = tableColumns.concat(graphSubmissionColumns);

            tableColumns.push({
                key: 'total_submissions',
                title: gettext('Total'),
                className: 'text-right',
                type: 'number',
                color: '#4BB4FB'
            });

            tableColumns.push({
                key: 'correct_percent',
                title: gettext('Percentage Correct'),
                className: 'text-right',
                type: 'percent'
            });

            if (model.get('hasSubmissions')) {
                new StackedBarView({
                    el: '#chart-view',
                    model: model,
                    modelAttribute: 'primaryContent',
                    truncateXTicks: true,
                    trends: graphSubmissionColumns,
                    x: {key: 'id', displayKey: 'name'},
                    y: {key: 'count'},
                    interactiveTooltipValueTemplate: function (trend) {
                        /* Translators: <%=value%> will be replaced by a number followed by a percentage.
                         For example, "400 (29%)" */
                        return _.template(gettext('<%=value%> (<%=percent%>)'))({
                            value: trend.value,
                            percent: d3.format('.1%')(trend.point[trend.options.percent_key])
                        });
                    },
                    click: function (d) {
                        if (_(d).has('url')) {
                            document.location.href = d.url;
                        }
                    }
                });
            }

            new DataTableView({
                el: '[data-role=performance-table]',
                model: model,
                modelAttribute: 'primaryContent',
                columns: tableColumns,
                sorting: ['index'],
                replaceZero: '-'
            });
        });
});
