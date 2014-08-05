/**
 * This is the first script called by the enrollment page.  It loads
 * the libraries and kicks off the application.
 */

// Load common.js first, which defines all of the models.  This is shared
// between pages.
require(['vendor/domReady!', 'load/init-page'], function(doc, page){
    'use strict';

    // this is your page specific code
    require(['views/attribute-listener-view',
            'views/attribute-view',
            'views/data-table-view',
            'views/enrollment-trend-view',
            'views/world-map-view'],
        function (AttributeListenerView, AttributeView, DataTableView,
                  EnrollmentTrendView, WorldMapView) {

        // Daily enrollment graph
        new EnrollmentTrendView({
            el: '#enrollment-trend-view',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentTrends'
        }).render();

        // Daily enrollment table
        new DataTableView({
            el: '[data-role=enrollment-table]',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentTrends',
            columns: [
                {key: 'date', title: 'Date'},
                {key: 'count', title: 'Count'}
            ],
            sorting: ['-date']
        });

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
                {key: 'countryName', title: 'Country'},
                {key: 'count', title: 'Count'}
            ],
            sorting: ['-count']
        });
        page.models.courseModel.fetchEnrollmentByCountry();
    });

});
