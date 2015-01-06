require(['vendor/domReady!', 'load/init-page'], function (doc, page) {
    'use strict';

    require(['underscore', 'views/data-table-view', 'views/stacked-bar-view'],
        function (_, DataTableView, StackedBarView) {
            var model = page.models.courseModel,
                assignmentType = model.get('assignmentType'),
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
                modelAttribute: 'assignments',
                trends: submissionColumns,
                x: {key: 'index'},
                y: {key: 'count'},
                interactiveTooltipHeaderTemplate: _.template(assignmentType + ' #<%=value%>')
            });

            var tableColumns = [
                    {key: 'index', title: gettext('Order'), type: 'number', className: 'text-right'},
                    {key: 'name', title: gettext('Assignment Name')},
                    {key: 'num_problems', title: gettext('Problems'), type: 'number', className: 'text-right'}
            ].concat(submissionColumns);

            new DataTableView({
                el: '[data-role=assignment-table]',
                model: model,
                modelAttribute: 'assignments',
                columns: tableColumns,
                sorting: ['index']
            });
        });
});
