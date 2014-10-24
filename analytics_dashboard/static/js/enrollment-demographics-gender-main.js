/**
 * This is the first script called by the enrollment demographics gender page.  It loads
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
            modelAttribute: 'genders',
            dataType: 'percent',
            trends: [{
                title: gettext('Gender'),
                color: 'rgb(58, 162, 224)'
            }],
            x: { key: 'gender' },
            y: { key: 'percent' }
        });

        // Daily enrollment table
        new DataTableView({
            el: '[data-role=enrollment-table]',
            model: page.models.courseModel,
            modelAttribute: 'genderTrend',
            columns: [
                {key: 'date', title: gettext('Date'), type: 'date'},
                {key: 'total', title: gettext('Total Enrollment'), className: 'text-right'},
                {key: 'female', title: gettext('Female'), className: 'text-right'},
                {key: 'male', title: gettext('Male'), className: 'text-right'},
                {key: 'other', title: gettext('Other'), className: 'text-right'},
                {key: 'unknown', title: gettext('Not Reported'), className: 'text-right'}
            ],
            sorting: ['-date']
        });
    });
});
