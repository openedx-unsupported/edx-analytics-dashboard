/**
 * This is the first script called by the engagement page.  It loads
 * the libraries and kicks off the application.
 */

require(['vendor/domReady!', 'load/init-page'], function (doc, page) {
    'use strict';

    require(['underscore', 'views/data-table-view', 'views/trends-view'], function (_, DataTableView, TrendsView) {
        // shared settings between the chart and table
        // colors are chosen to be color-blind accessible
        var settings = [
                {
                    key: 'weekEnding',
                    title: gettext('Week Ending'),
                    type: 'date'
                },
                {
                    key: 'any',
                    title: gettext('Active Students'),
                    color: '#8DA0CB',
                    className: 'text-right',
                    type: 'number'
                },
                {
                    key: 'played_video',
                    title: gettext('Watched a Video'),
                    color: '#66C2A5',
                    className: 'text-right',
                    type: 'number'
                },
                {
                    key: 'attempted_problem',
                    title: gettext('Tried a Problem'),
                    color: '#FC8D62',
                    className: 'text-right',
                    type: 'number'
                },
                {
                    key: 'posted_forum',
                    title: gettext('Posted in Forum'),
                    color: '#E78AC3',
                    className: 'text-right',
                    type: 'number'
                }
            ],
            trendSettings;

        // remove settings for data that doesn't exist (ex. forums)
        settings = _(settings).filter(function (setting) {
            return page.models.courseModel.hasTrend('engagementTrends', setting.key);
        });

        // trend settings don't need weekEnding
        trendSettings = _(settings).filter(function (setting) {
            return setting.key !== 'weekEnding';
        });

        // weekly engagement activities graph
        new TrendsView({
            el: '#engagement-trend-view',
            model: page.models.courseModel,
            modelAttribute: 'engagementTrends',
            trends: trendSettings,
            x: {
                // displayed on the axis
                title: 'Date',
                // key in the data
                key: 'weekEnding'
            },
            y: {
                title: 'Students',
                key: 'count'
            },
            // Translators: <%=value%> will be replaced with a date.
            interactiveTooltipHeaderTemplate: _.template(gettext('Week Ending <%=value%>'))
        });

        // weekly engagement activities table
        new DataTableView({
            el: '[data-role=engagement-table]',
            model: page.models.courseModel,
            modelAttribute: 'engagementTrends',
            columns: settings,
            sorting: ['-weekEnding']
        });
    });
});
