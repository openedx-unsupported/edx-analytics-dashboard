/**
 * This is the first script called by the enrollment demographics education page.  It loads
 * the libraries and kicks off the application.
 */

require(['load/init-page'], function(page) {
    'use strict';

    require(['underscore', 'views/data-table-view', 'views/discrete-bar-view'],
        function(_, DataTableView, DiscreteBarView) {
            var educationChart = new DiscreteBarView({
                    el: '#enrollment-chart-view',
                    model: page.models.courseModel,
                    modelAttribute: 'education',
                    excludeData: ['Unknown'],
                    dataType: 'percent',
                    trends: [{
                        title: gettext('Percentage'),
                        color: 'rgb(58, 162, 224)'
                    }],
                    x: {key: 'educationLevel'},
                    y: {key: 'percent'},
                    // Translators: <%=value%> will be replaced with a level of education (e.g. Doctorate).
                    interactiveTooltipHeaderTemplate: _.template(gettext('Education: <%=value%>'))
                }),
                educationTable = new DataTableView({
                    el: '[data-role=enrollment-table]',
                    model: page.models.courseModel,
                    modelAttribute: 'education',
                    columns: [
                        {key: 'educationLevel', title: gettext('Educational Background')},
                        {key: 'count', title: gettext('Number of Learners'), type: 'number', className: 'text-right'}
                    ],
                    sorting: ['-count']
                });

            educationChart.renderIfDataAvailable();
            educationTable.renderIfDataAvailable();
        });
});
