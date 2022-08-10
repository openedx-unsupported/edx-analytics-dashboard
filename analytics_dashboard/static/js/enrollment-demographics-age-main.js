/**
 * This is the first script called by the enrollment demographics age page.  It loads
 * the libraries and kicks off the application.
 */
const _ = require('underscore');
const DataTableView = require('views/data-table-view');
const HistogramView = require('views/histogram-view');

require(['load/init-page'], (page) => {
  'use strict';

  // used in the table to show ages above this are binned--displayed as "100+"
  const maxNumber = 100;
  const ageChart = new HistogramView({
    el: '#enrollment-chart-view',
    model: page.models.courseModel,
    modelAttribute: 'ages',
    excludeData: [gettext('Unknown')],
    trends: [{
      title: gettext('Number of Learners'),
      color: 'rgb(58, 162, 224)',
      maxNumber,
    }],
    x: { key: 'age' },
    y: { key: 'count' },
    // Translators: <%=value%> will be replaced with an age.
    interactiveTooltipHeaderTemplate: _.template(gettext('Age: <%=value%>')),
  });
  const ageTable = new DataTableView({
    el: '[data-role=enrollment-table]',
    model: page.models.courseModel,
    modelAttribute: 'ages',
    columns: [
      {
        key: 'age', title: gettext('Age'), type: 'maxNumber', maxNumber,
      },
      {
        key: 'count', title: gettext('Number of Learners'), type: 'number', className: 'text-right',
      },
      {
        key: 'percent', title: gettext('Percent of Total'), type: 'percent', className: 'text-right',
      },
    ],
    sorting: ['-percent'],
  });
  ageChart.renderIfDataAvailable();
  ageTable.renderIfDataAvailable();
});
