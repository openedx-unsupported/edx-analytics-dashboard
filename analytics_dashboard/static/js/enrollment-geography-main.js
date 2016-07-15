/**
 * This is the first script called by the enrollment geography page.  It loads
 * the libraries and kicks off the application.
 */
var doc = require('vendor/domReady!'),
    page = require('load/init-page'),
    DataTableView = require('views/data-table-view'),
    WorldMapView = require('views/world-map-view');

(function() {
    'use strict';

    // this is your page specific code
    (function() {
        // Enrollment by country map
        new WorldMapView({
            el: '[data-view=world-map]',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentByCountry',
            // eslint-disable-next-line max-len
            tooltip: gettext('Student location is determined from IP address. This map shows where students most recently connected.')
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
                {key: 'count', title: gettext('Current Enrollment'), className: 'text-right', type: 'number'}
            ],
            sorting: ['-count']
        });
    });
});
