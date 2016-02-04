/**
 * This is the first script called by the enrollment demographics age page.  It loads
 * the libraries and kicks off the application.
 */

require(['vendor/domReady!', 'load/init-page'], function(doc, page) {
    'use strict';

    require(['underscore', 'views/data-table-view', 'views/histogram-view'],
        function (_, DataTableView, HistogramView) {

            // used in the table to show ages above this are binned--displayed as "100+"
            var maxNumber = 100;

            new HistogramView({
                el: '#enrollment-chart-view',
                model: page.models.courseModel,
                modelAttribute: 'ages',
                excludeData: ['Unknown'],
                trends: [{
                    title: gettext('Number of Students'),
                    color: 'rgb(58, 162, 224)',
                    maxNumber: maxNumber
                }],
                x: { key: 'age' },
                y: { key: 'count' },
                // Translators: <%=value%> will be replaced with an age.
                interactiveTooltipHeaderTemplate: _.template(gettext('Age: <%=value%>'))
            });

            new DataTableView({
                el: '[data-role=enrollment-table]',
                model: page.models.courseModel,
                modelAttribute: 'ages',
                columns: [
                    {key: 'age', title: gettext('Age'), type: 'maxNumber', maxNumber: maxNumber},
                    {key: 'count', title: gettext('Number of Students'), type: 'number', className: 'text-right'},
                    {key: 'percent', title: gettext('Percent of Total'), type: 'percent', className: 'text-right'}
                ],
                sorting: ['-percent']
            });
        });
});
