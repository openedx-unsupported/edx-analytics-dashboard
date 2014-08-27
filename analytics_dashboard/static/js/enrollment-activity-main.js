/**
 * This is the first script called by the enrollment activity page.  It loads
 * the libraries and kicks off the application.
 */

require(['vendor/domReady!', 'load/init-page'], function(doc, page){
    'use strict';

    // this is your page specific code
    require(['views/data-table-view',
            'views/enrollment-trend-view'],
        function (DataTableView, EnrollmentTrendView) {

        // Daily enrollment graph
        new EnrollmentTrendView({
            el: '#enrollment-trend-view',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentTrends'
        });

        // Daily enrollment table
        new DataTableView({
            el: '[data-role=enrollment-table]',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentTrends',
            columns: [
                {key: 'date', title: gettext('Date'), type: 'date'},
                // Translators: The noun count (e.g. number of students)
                {key: 'count', title: gettext('Total Enrollment'), className: 'text-right'}
            ],
            sorting: ['-date']
        });
    });

});
