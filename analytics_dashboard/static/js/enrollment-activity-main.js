/**
 * This is the first script called by the enrollment activity page.  It loads
 * the libraries and kicks off the application.
 */
var doc = require('vendor/domReady!'),
    _ = require('underscore'),
    page = require('load/init-page'),
    DataTableView = require('views/data-table-view'),
    StackedTrendsView = require('views/stacked-trands-view');

(function() {
    'use strict';
    (function() {
        var colors = ['#4BB4FB', '#CA0061', '#CCCCCC'],
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
                    color: colors[0]
                }),
                _.defaults({}, numericColumn, {
                    key: 'audit',
                    title: gettext('Audit'),
                    color: colors[0]
                }),
                _.defaults({}, numericColumn, {
                    key: 'verified',
                    title: gettext('Verified'),
                    color: colors[1]
                }),
                _.defaults({}, numericColumn, {
                    key: 'professional',
                    title: gettext('Professional'),
                    color: colors[2]
                }),
                _.defaults({}, numericColumn, {
                    key: 'credit',
                    // Translators: this label indicates the learner has registered for academic credit
                    title: gettext('Verified with Credit'),
                    color: colors[2]
                })
            ],
            trendSettings,
            enrollmentTrackTrendSettings;

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
        new StackedTrendsView({
            el: '#enrollment-trend-view',
            model: page.models.courseModel,
            modelAttribute: 'enrollmentTrends',
            trends: trendSettings,
            x: {key: 'date'},
            y: {key: 'count'}
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
