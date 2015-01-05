require(['vendor/domReady!', 'load/init-page'], function (doc, page) {
    'use strict';

    require(['underscore', 'views/data-table-view', 'views/stacked-bar-view'],
        function (_, DataTableView, StackedBarView) {
            var model = page.models.courseModel,
                submissionColumns = [
                    {
                        key: 'total_submissions',
                        title: gettext('Total Submissions'),
                        className: 'text-right',
                        type: 'number',
                        color: '#4BB4FB'
                    },
                    {
                        key: 'correct_submissions',
                        title: gettext('Correct Submissions'),
                        className: 'text-right',
                        type: 'number',
                        color: '#CA0061'
                    }
                ];

            new StackedBarView({
                el: '#chart-view',
                model: model,
                modelAttribute: 'problems',
                trends: submissionColumns,
                x: {key: 'order'},
                y: {key: 'count'},
                interactiveTooltipHeaderTitleKey: 'name'
            });

            var tableColumns = [
                    {key: 'order', title: gettext('Order'), type: 'number', className: 'text-right'},
                    {key: 'name', title: gettext('Problem Name')}
            ].concat(submissionColumns);

            new DataTableView({
                el: '[data-role=problem-table]',
                model: model,
                modelAttribute: 'problems',
                columns: tableColumns,
                sorting: ['order']
            });
        });
});
