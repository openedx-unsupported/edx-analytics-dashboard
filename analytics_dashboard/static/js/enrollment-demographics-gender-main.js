/**
 * This is the first script called by the enrollment demographics gender page.  It loads
 * the libraries and kicks off the application.
 */
const _ = require('underscore');
const DataTableView = require('views/data-table-view');
const DiscreteBarView = require('views/discrete-bar-view');

require(['load/init-page'], (page) => {
  'use strict';

  const genderChart = new DiscreteBarView({
    el: '#enrollment-chart-view',
    model: page.models.courseModel,
    modelAttribute: 'genders',
    dataType: 'percent',
    trends: [{
      title: gettext('Percentage'),
      color: 'rgb(58, 162, 224)',
    }],
    x: { key: 'gender' },
    y: { key: 'percent' },
    // Translators: <%=value%> will be replaced with a level of gender (e.g. Female).
    interactiveTooltipHeaderTemplate: _.template(gettext('Gender: <%=value%>')),
  });
  // Daily enrollment table
  const genderTable = new DataTableView({
    el: '[data-role=enrollment-table]',
    model: page.models.courseModel,
    modelAttribute: 'genderTrend',
    columns: [
      { key: 'date', title: gettext('Date'), type: 'date' },
      {
        key: 'total', title: gettext('Current Enrollment'), type: 'number', className: 'text-right',
      },
      {
        key: 'female', title: gettext('Female'), type: 'number', className: 'text-right',
      },
      {
        key: 'male', title: gettext('Male'), type: 'number', className: 'text-right',
      },
      {
        key: 'other', title: gettext('Other'), type: 'number', className: 'text-right',
      },
      {
        key: 'unknown', title: gettext('Not Reported'), type: 'number', className: 'text-right',
      },
    ],
    sorting: ['-date'],
  });

  genderChart.renderIfDataAvailable();
  genderTable.renderIfDataAvailable();
});
