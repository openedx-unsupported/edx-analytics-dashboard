/**
 * This is the first script called by the enrollment demographics education page.  It loads
 * the libraries and kicks off the application.
 */

require(['vendor/domReady!', 'load/init-page'], function(doc, page) {
    'use strict';

    require(['views/data-table-view',
            'views/discrete-bar-view'],
        function (DataTableView, DiscreteBarView) {

        new DiscreteBarView({
            el: '#enrollment-chart-view',
            model: page.models.courseModel,
            modelAttribute: 'education',
            excludeData: ['Unknown'],
            dataType: 'percent',
            trends: [{
                title: 'Education',
                color: 'rgb(58, 162, 224)'
            }],
            x: { key: 'educationLevelShort' },
            y: { key: 'percent' }
        });

        new DataTableView({
            el: '[data-role=enrollment-table]',
            model: page.models.courseModel,
            modelAttribute: 'education',
            columns: [
                {key: 'educationLevelLong', title: gettext('Educational Background')},
                {key: 'count', title: gettext('Total Enrollment'), className: 'text-right'}
            ],
            sorting: ['-count']
        });
    });
});
