/**
 * This is the first script called by the video timeline page and displays a
 * video timeline chart and data table.
 */
require(['load/init-page'], (page) => {
  'use strict';

  require([
    'edx-ui-toolkit/src/js/disclosure/disclosure-view',
    'underscore',
    'views/data-table-view',
    'views/iframe-view',
    'views/stacked-timeline-view',
  ], (
    DisclosureView,
    _,
    DataTableView,
    IFrameView,
    StackedTimelineView,
  ) => {
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
    let iframe;
    let videoTimelineChart;
    let videoTimelineTable;

    tableColumns = tableColumns.concat(timelineSettings);

    new DisclosureView({ // eslint-disable-line no-new
      el: '.module-preview-disclosure',
    });

    // loading the iframe blocks content, so load it after the rest of the page loads
    iframe = new IFrameView({
      el: '#module-preview',
      loadingSelector: '#module-loading',
    });
    iframe.render();

    videoTimelineChart = new StackedTimelineView({
      el: '#chart-view',
      model: courseModel,
      modelAttribute: 'videoTimeline',
      trends: timelineSettings,
      x: { key: 'start_time', title: 'Time' },
      y: { key: 'num_users' },
    });
    videoTimelineChart.renderIfDataAvailable();

    videoTimelineTable = new DataTableView({
      el: '[data-role=data-table]',
      model: courseModel,
      modelAttribute: 'videoTimeline',
      columns: tableColumns,
    });
    videoTimelineTable.renderIfDataAvailable();
  });
});
