/**
 * This is the first script called by the enrollment geography page.  It loads
 * the libraries and kicks off the application.
 */
const DataTableView = require('views/data-table-view');
const WorldMapView = require('views/world-map-view');

require(['load/init-page'], (page) => {
  'use strict';

  // this is your page specific code
  // Enrollment by country map
  const enrollmentGeographyMap = new WorldMapView({
    el: '[data-view=world-map]',
    model: page.models.courseModel,
    modelAttribute: 'enrollmentByCountry',
    // eslint-disable-next-line max-len
    tooltip: gettext('Learner location is determined from IP address. This map shows where learners most recently connected.'),
  });
  // Enrollment by country table
  const enrollmentGeographyTable = new DataTableView({
    el: '[data-role=enrollment-location-table]',
    model: page.models.courseModel,
    modelAttribute: 'enrollmentByCountry',
    columns: [
      { key: 'countryName', title: gettext('Country or Region') },
      {
        key: 'percent', title: gettext('Percent'), className: 'text-right', type: 'percent',
      },
      // Translators: The noun count (e.g. number of learners)
      {
        key: 'count', title: gettext('Current Enrollment'), className: 'text-right', type: 'number',
      },
    ],
    sorting: ['-count'],
  });
  enrollmentGeographyTable.renderIfDataAvailable();
  enrollmentGeographyMap.renderIfDataAvailable();
});
