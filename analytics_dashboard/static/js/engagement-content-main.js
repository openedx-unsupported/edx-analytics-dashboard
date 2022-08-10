/**
 * This is the first script called by the engagement page.  It loads
 * the libraries and kicks off the application.
 */
const _ = require('underscore');
const DataTableView = require('views/data-table-view');
const TrendsView = require('views/trends-view');

require(['load/init-page'], (page) => {
  'use strict';

  // shared settings between the chart and table
  // colors are chosen to be color-blind accessible
  let settings = [
    {
      key: 'weekEnding',
      title: gettext('Week Ending'),
      type: 'date',
    },
    {
      key: 'any',
      title: gettext('Active Learners'),
      color: '#8DA0CB',
      className: 'text-right',
      type: 'number',
    },
    {
      key: 'played_video',
      title: gettext('Watched a Video'),
      color: '#66C2A5',
      className: 'text-right',
      type: 'number',
    },
    {
      key: 'attempted_problem',
      title: gettext('Tried a Problem'),
      color: '#FC8D62',
      className: 'text-right',
      type: 'number',
    },
    {
      key: 'posted_forum',
      title: gettext('Participated in Discussions'),
      color: '#E78AC3',
      className: 'text-right',
      type: 'number',
    },
    {
      key: 'active_percent',
      title: gettext('Percent of Current Learners'),
      color: '#FFFFFF',
      className: 'text-right',
      type: 'percent',
    },
  ];

  // remove settings for data that doesn't exist (ex. forums)
  settings = _(settings).filter((setting) => page.models.courseModel.hasTrend('engagementTrends', setting.key));

  // trend settings don't need weekEnding
  const trendSettings = _(settings).filter((setting) => setting.key !== 'weekEnding' && setting.key !== 'active_percent');

  // weekly engagement activities graph
  const engagementChart = new TrendsView({
    el: '#engagement-trend-view',
    model: page.models.courseModel,
    modelAttribute: 'engagementTrends',
    trends: trendSettings,
    x: {
      // displayed on the axis
      title: 'Date',
      // key in the data
      key: 'weekEnding',
    },
    y: {
      title: 'Learners',
      key: 'count',
    },
    // Translators: <%=value%> will be replaced with a date.
    interactiveTooltipHeaderTemplate: _.template(gettext('Week Ending <%=value%>')),
  });
  engagementChart.renderIfDataAvailable();

  // weekly engagement activities table
  const engagementTable = new DataTableView({
    el: '[data-role=engagement-table]',
    model: page.models.courseModel,
    modelAttribute: 'engagementTrends',
    columns: settings,
    sorting: ['-weekEnding'],
    replaceNull: '-',
  });
  engagementTable.renderIfDataAvailable();
});
