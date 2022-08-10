require('d3');
require('underscore');
const DataTableView = require('views/data-table-view');
const StackedBarView = require('views/stacked-bar-view');

require(['load/init-page'], (page) => {
  'use strict';

  const model = page.models.courseModel;
  const graphSubmissionColumns = [
    {
      key: 'average_correct_submissions',
      percent_key: 'correct_percent',
      title: gettext('Average Correct'),
      className: 'text-right',
      type: 'number',
      fractionDigits: 1,
      color: '#4BB4FB',
    },
    {
      key: 'average_incorrect_submissions',
      percent_key: 'incorrect_percent',
      title: gettext('Average Incorrect'),
      className: 'text-right',
      type: 'number',
      fractionDigits: 1,
      color: '#CA0061',
    },
  ];
  let tableColumns = [
    {
      key: 'index', title: gettext('Order'), type: 'number', className: 'text-right',
    },
    { key: 'name', title: model.get('contentTableHeading'), type: 'hasNull' },
    {
      key: 'num_modules', title: gettext('Problems'), type: 'number', className: 'text-right',
    },
  ];
  let performanceChart;

  tableColumns = tableColumns.concat(graphSubmissionColumns);

  tableColumns.push({
    key: 'average_submissions',
    title: gettext('Average Submissions Per Problem'),
    className: 'text-right',
    type: 'number',
    fractionDigits: 1,
    color: '#4BB4FB',
  });

  tableColumns.push({
    key: 'correct_percent',
    title: gettext('Percentage Correct'),
    className: 'text-right',
    type: 'percent',
  });

  if (model.get('hasData')) {
    performanceChart = new StackedBarView({
      el: '#chart-view',
      model,
      modelAttribute: 'primaryContent',
      dataType: 'decimal',
      trends: graphSubmissionColumns,
    });
    performanceChart.renderIfDataAvailable();
  }

  const performanceTable = new DataTableView({
    el: '[data-role=data-table]',
    model,
    modelAttribute: 'primaryContent',
    columns: tableColumns,
    sorting: ['index'],
    replaceZero: '-',
  });
  performanceTable.renderIfDataAvailable();
});
