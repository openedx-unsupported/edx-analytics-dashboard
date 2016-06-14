/**
 * This is the first script called by the engagement page.  It loads
 * the libraries and kicks off the application.
 */

require(['vendor/domReady!', 'load/init-page'], function (doc, page) {
    'use strict';

    require(['underscore', 'views/data-table-view', 'views/trends-view', 'views/stacked-bar-view'],
        function (_, DataTableView, TrendsView, StackedBarView) {
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
                },
                {
                    key: 'active_percent',
                    title: gettext('Percent of Current Students'),
                    color: '#FFFFFF',
                    className: 'text-right',
                    type: 'percent'
                }
            ],
            trendSettings,
            courseViewsColumns;

        // remove settings for data that doesn't exist (ex. forums)
        settings = _(settings).filter(function (setting) {
            return page.models.courseModel.hasTrend('engagementTrends', setting.key);
        });

        // trend settings don't need weekEnding
        trendSettings = _(settings).filter(function (setting) {
            return setting.key !== 'weekEnding' && setting.key !== 'active_percent';
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
            sorting: ['-weekEnding'],
            replaceNull: '-'
        });

        courseViewsColumns = [
            {
                key: 'total_views',
                title: gettext('Average Correct'),
                className: 'text-right',
                type: 'number',
                color: '#4BB4FB'
            },
            {
                key: 'unique_user_views',
                title: gettext('Average Incorrect'),
                className: 'text-right',
                type: 'number',
                color: '#CA0061'
            }
        ];
        // create a unique name...
        _(page.models.courseModel.get('courseViews')).each(function (view) {
            view.name = [view.section, view.subsection].join('_');
        });

        new StackedBarView({
            el: '#course-views',
            model: page.models.courseModel,
            modelAttribute: 'courseViews',
            trends: courseViewsColumns
        });

    });
});
