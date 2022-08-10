/**
 * Called for displaying a collection of video charts and tables.  Each bar represents a single video.
 */
require('d3');
require('underscore');
const DataTableView = require('views/data-table-view');
const StackedBarView = require('views/stacked-bar-view');

require(['load/init-page'], (page) => {
  'use strict';

  const model = page.models.courseModel;
  const graphVideoColumns = [
    {
      key: 'users_at_end',
      percent_key: 'end_percent',
      title: gettext('Complete Views'),
      className: 'text-right',
      type: 'number',
      color: '#58BC4B',
    },
    {
      key: 'start_only_users',
      percent_key: 'start_only_percent',
      title: gettext('Incomplete Views'),
      className: 'text-right',
      type: 'number',
      color: '#9B9B9B',
    },
  ];
  let tableColumns = [
    {
      key: 'index', title: gettext('Order'), type: 'number', className: 'text-right',
    },
    { key: 'name', title: model.get('contentTableHeading'), type: 'hasNull' },
  ];
  let videoChart;

  tableColumns = tableColumns.concat(graphVideoColumns);
  tableColumns.push({
    key: 'end_percent',
    title: gettext('Completion Percentage'),
    className: 'text-right',
    type: 'percent',
  });

  if (model.get('hasData')) {
    videoChart = new StackedBarView({
      el: '#chart-view',
      model,
      modelAttribute: 'primaryContent',
      trends: graphVideoColumns,
    });
    videoChart.renderIfDataAvailable();
  }

  const videoTable = new DataTableView({
    el: '[data-role=data-table]',
    model,
    modelAttribute: 'primaryContent',
    columns: tableColumns,
    sorting: ['index'],
    replaceZero: '-',
  });
  videoTable.renderIfDataAvailable();
});
