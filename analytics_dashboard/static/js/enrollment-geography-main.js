/**
 * This is the first script called by the enrollment geography page.  It loads
 * the libraries and kicks off the application.
 */

require(['vendor/domReady!', 'load/init-page'], function(doc, page){
    'use strict';

    // this is your page specific code
    require(['views/attribute-view',
            'views/data-table-view',
            'views/world-map-view'],
        function (AttributeView, DataTableView,
                  WorldMapView) {

        // Enrollment by country last updated label
        new AttributeView({
            el: '[data-view=enrollment-by-country-update-date]',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentByCountryUpdateDate'
        });

        // Enrollment by country map
        new WorldMapView({
            el: '[data-view=world-map]',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentByCountry'
        });

        // Enrollment by country table
        new DataTableView({
            el: '[data-role=enrollment-location-table]',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentByCountry',
            columns: [
                {key: 'countryName', title: gettext('Country')},
                // Translators: The noun count (e.g. number of students)
                {key: 'count', title: gettext('Count')}
            ],
            sorting: ['-count']
        });
    });
});
