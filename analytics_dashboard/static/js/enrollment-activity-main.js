/**
 * This is the first script called by the enrollment activity page.  It loads
 * the libraries and kicks off the application.
 */
import _, { defaults } from 'underscore';
import DataTableView from 'views/data-table-view';
import StackedTrendsView from 'views/stacked-trends-view';
import page from 'load/init-page';

define(() => {
  'use strict';

  // this is your page specific code
  const colors = ['#4BB4FB', '#898C8F', '#009CD3', '#B72667', '#442255', '#1E8142'];
  const numericColumn = {
    className: 'text-right',
    type: 'number',
  };
  let settings = [
    {
      key: 'date',
      title: gettext('Date'),
      type: 'date',
    },
    defaults({}, numericColumn, {
      key: 'count',
      title: gettext('Current Enrollment'),
      color: colors[0],
    }),
    defaults({}, numericColumn, {
      key: 'honor',
      // Translators: this describe the learner's enrollment track (e.g. Honor certificate)
      title: gettext('Honor'),
      color: colors[1],
    }),
    defaults({}, numericColumn, {
      key: 'audit',
      title: gettext('Audit'),
      color: colors[2],
    }),
    defaults({}, numericColumn, {
      key: 'verified',
      title: gettext('Verified'),
      color: colors[3],
    }),
    defaults({}, numericColumn, {
      key: 'professional',
      title: gettext('Professional'),
      color: colors[4],
    }),
    defaults({}, numericColumn, {
      key: 'credit',
      // Translators: this label indicates the learner has registered for academic credit
      title: gettext('Verified with Credit'),
      color: colors[5],
    }),
  ];
  let trendSettings;

  // Remove settings for which there is no data (e.g. don't attempt to display verified if there is no data).
  settings = _(settings).filter((setting) => page.models.courseModel.hasTrend('enrollmentTrends', setting.key));

  trendSettings = _(settings).filter((setting) => setting.key !== 'date');

  // Do not display total enrollment on the chart if track data exists
  const enrollmentTrackTrendSettings = _(trendSettings).filter((setting) => setting.key !== 'count');

  if (enrollmentTrackTrendSettings.length) {
    trendSettings = enrollmentTrackTrendSettings;
  }

  // Daily enrollment graph
  const enrollmentChart = new StackedTrendsView({
    el: '#enrollment-trend-view',
    model: page.models.courseModel,
    modelAttribute: 'enrollmentTrends',
    trends: trendSettings,
    x: { key: 'date' },
    y: { key: 'count' },
  });
  enrollmentChart.renderIfDataAvailable();

  // Daily enrollment table
  const enrollmentTable = new DataTableView({
    el: '[data-role=enrollment-table]',
    model: page.models.courseModel,
    modelAttribute: 'enrollmentTrends',
    columns: settings,
    sorting: ['-date'],
  });
  enrollmentTable.renderIfDataAvailable();
});
