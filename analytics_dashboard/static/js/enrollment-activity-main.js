/**
 * This is the first script called by the enrollment activity page.  It loads
 * the libraries and kicks off the application.
 */

require(['vendor/domReady', 'load/init-page'], function(doc, page) {
    'use strict';

    // this is your page specific code
    require(['underscore',
            'views/data-table-view',
            'views/stacked-trends-view'],
    function(_, DataTableView, StackedTrendsView) {
        var colors = ['#4BB4FB', '#898C8F', '#009CD3', '#B72667', '#442255', '#1E8142'],
            numericColumn = {
                className: 'text-right',
                type: 'number'
            },
            settings = [
                {
                    key: 'date',
                    title: gettext('Date'),
                    type: 'date'
                },
                _.defaults({}, numericColumn, {
                    key: 'count',
                    title: gettext('Current Enrollment'),
                    color: colors[0]
                }),
                _.defaults({}, numericColumn, {
                    key: 'honor',
                    // Translators: this describe the learner's enrollment track (e.g. Honor certificate)
                    title: gettext('Honor'),
                    color: colors[1]
                }),
                _.defaults({}, numericColumn, {
                    key: 'audit',
                    title: gettext('Audit'),
                    color: colors[2]
                }),
                _.defaults({}, numericColumn, {
                    key: 'verified',
                    title: gettext('Verified'),
                    color: colors[3]
                }),
                _.defaults({}, numericColumn, {
                    key: 'professional',
                    title: gettext('Professional'),
                    color: colors[4]
                }),
                _.defaults({}, numericColumn, {
                    key: 'credit',
                    // Translators: this label indicates the learner has registered for academic credit
                    title: gettext('Verified with Credit'),
                    color: colors[5]
                })
            ],
            trendSettings,
            enrollmentTrackTrendSettings,
            enrollmentChart,
            enrollmentTable;

        // Remove settings for which there is no data (e.g. don't attempt to display verified if there is no data).
        settings = _(settings).filter(function(setting) {
            return page.models.courseModel.hasTrend('enrollmentTrends', setting.key);
        });

        trendSettings = _(settings).filter(function(setting) {
            return setting.key !== 'date';
        });

        // Do not display total enrollment on the chart if track data exists
        enrollmentTrackTrendSettings = _(trendSettings).filter(function(setting) {
            return setting.key !== 'count';
        });

        if (enrollmentTrackTrendSettings.length) {
            trendSettings = enrollmentTrackTrendSettings;
        }

        // Daily enrollment graph
        enrollmentChart = new StackedTrendsView({
            el: '#enrollment-trend-view',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentTrends',
            trends: trendSettings,
            x: {key: 'date'},
            y: {key: 'count'}
        });
        enrollmentChart.renderIfDataAvailable();

        // Daily enrollment table
        enrollmentTable = new DataTableView({
            el: '[data-role=enrollment-table]',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentTrends',
            columns: settings,
            sorting: ['-date']
        });
        enrollmentTable.renderIfDataAvailable();
    });
});
