/**
 * This is the first script called by the enrollment activity page.  It loads
 * the libraries and kicks off the application.
 */

require(['vendor/domReady!', 'load/init-page'], function(doc, page){
    'use strict';

    // this is your page specific code
    require(['views/data-table-view',
            'views/trends-view'],
        function (DataTableView, TrendsView) {

        // Daily enrollment graph
        new TrendsView({
            el: '#enrollment-trend-view',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentTrends',
            trends: [{title: 'Students'}],
            x: { key: 'date' },
            y: { key: 'count' },
            tooltip: gettext('This graph displays total enrollment for the course calculated at the end of each day. Total enrollment includes new enrollments as well as unenrollments.')
        });

        // Daily enrollment table
        new DataTableView({
            el: '[data-role=enrollment-table]',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentTrends',
            columns: [
                {key: 'date', title: gettext('Date'), type: 'date'},
                // Translators: The noun count (e.g. number of students)
                {key: 'count', title: gettext('Total Enrollment'), className: 'text-right', type: 'number'}
            ],
            sorting: ['-date']
        });
    });
});
