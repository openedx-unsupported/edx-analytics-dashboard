/**
 * This is the first script called by the video timeline page and displays a
 * video timeline chart and data table.
 */
require('underscore');
const DisclosureView = require('edx-ui-toolkit/src/js/disclosure/disclosure-view');
const DataTableView = require('views/data-table-view');
const IFrameView = require('views/iframe-view');
const StackedTimelineView = require('views/stacked-timeline-view');

require(['load/init-page'], (page) => {
  'use strict';

  const { courseModel } = page.models;
  const timelineSettings = [
    {
      key: 'num_users',
      title: gettext('Unique Viewers'),
      className: 'text-right',
      type: 'number',
      color: 'rgb(61,162,229)',
    },
    {
      key: 'num_replays',
      title: gettext('Replays'),
      className: 'text-right',
      type: 'number',
      color: 'rgb(18,46,204)',
    },
  ];
  let tableColumns = [
    { key: 'start_time', title: gettext('Time'), type: 'time' },
  ];

  tableColumns = tableColumns.concat(timelineSettings);

  new DisclosureView({ // eslint-disable-line no-new
    el: '.module-preview-disclosure',
  });

  // loading the iframe blocks content, so load it after the rest of the page loads
  const iframe = new IFrameView({
    el: '#module-preview',
    loadingSelector: '#module-loading',
  });
  iframe.render();

  const videoTimelineChart = new StackedTimelineView({
    el: '#chart-view',
    model: courseModel,
    modelAttribute: 'videoTimeline',
    trends: timelineSettings,
    x: { key: 'start_time', title: 'Time' },
    y: { key: 'num_users' },
  });
  videoTimelineChart.renderIfDataAvailable();

  const videoTimelineTable = new DataTableView({
    el: '[data-role=data-table]',
    model: courseModel,
    modelAttribute: 'videoTimeline',
    columns: tableColumns,
  });
  videoTimelineTable.renderIfDataAvailable();
});
