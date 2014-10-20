/**
 * This is the first script called by the enrollment geography page.  It loads
 * the libraries and kicks off the application.
 */

require(['vendor/domReady!', 'load/init-page'], function (doc, page) {
    'use strict';

    // this is your page specific code
    require(['views/data-table-view', 'views/world-map-view'],
        function (DataTableView, WorldMapView) {
            // Enrollment by country map
            new WorldMapView({
                el: '[data-view=world-map]',
                model: page.models.courseModel,
                modelAttribute: 'enrollmentByCountry',
                tooltip: gettext('Student location is determined from IP address. This map shows where students most recently connected.')  // jshint ignore:line
            });

            // Enrollment by country table
            new DataTableView({
                el: '[data-role=enrollment-location-table]',
                model: page.models.courseModel,
                modelAttribute: 'enrollmentByCountry',
                columns: [
                    {key: 'countryName', title: gettext('Country')},
                    {key: 'percent', title: gettext('Percent'), className: 'text-right', type: 'percent'},
                    // Translators: The noun count (e.g. number of students)
                    {key: 'count', title: gettext('Total Enrollment'), className: 'text-right', type: 'number'}
                ],
                sorting: ['-count']
            });
        }
    );
});
