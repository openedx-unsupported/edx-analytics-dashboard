/**
 * This is the first script called by the enrollment activity page.  It loads
 * the libraries and kicks off the application.
 */

require(['vendor/domReady!', 'load/init-page'], function (doc, page) {
    'use strict';

    // this is your page specific code
    require(['views/data-table-view',
            'views/stacked-trends-view'],
        function (DataTableView, StackedTrendsView) {

            var settings = [
                    {
                        key: 'date',
                        title: gettext('Date'),
                        type: 'date'
                    },
                    {
                        key: 'count',
                        title: gettext('Total Enrollment'),
                        className: 'text-right',
                        type: 'number',
                        color: '#4BB4FB'
                    },
                    {
                        key: 'honor',
                        title: gettext('Honor Code'),
                        className: 'text-right',
                        type: 'number',
                        color: '#4BB4FB'
                    },
                    {
                        key: 'verified',
                        title: gettext('Verified'),
                        className: 'text-right',
                        type: 'number',
                        color: '#CA0061'
                    },
                    {
                        key: 'professional',
                        title: gettext('Professional'),
                        className: 'text-right',
                        type: 'number',
                        color: '#CCCCCC'
                    }
                ],
                trendSettings,
                enrollmentTrackTrendSettings;

            // Remove settings for which there is no data (e.g. don't attempt to display verified if there is no data).
            settings = _(settings).filter(function (setting) {
                return page.models.courseModel.hasTrend('enrollmentTrends', setting.key);
            });

            trendSettings = _(settings).filter(function (setting) {
                return setting.key !== 'date';
            });

            // Do not display total enrollment on the chart if track data exists
            enrollmentTrackTrendSettings = _(trendSettings).filter(function (setting) {
                return setting.key !== 'count';
            });

            if (enrollmentTrackTrendSettings.length) {
                trendSettings = enrollmentTrackTrendSettings;
            }

            // Daily enrollment graph
            new StackedTrendsView({
                el: '#enrollment-trend-view',
                model: page.models.courseModel,
                modelAttribute: 'enrollmentTrends',
                trends: trendSettings,
                x: { key: 'date' },
                y: { key: 'count' }
            });

            // Daily enrollment table
            new DataTableView({
                el: '[data-role=enrollment-table]',
                model: page.models.courseModel,
                modelAttribute: 'enrollmentTrends',
                columns: settings,
                sorting: ['-date']
            });
        });
});
