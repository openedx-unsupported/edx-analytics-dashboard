/**
 * This is the first script called by the video timeline page and displays a
 * video timeline chart and data table.
 */
require(['vendor/domReady!', 'load/init-page'], function(doc, page) {
    'use strict';

    require(['disclosure', 'underscore', 'views/data-table-view', 'views/iframe-view', 'views/stacked-timeline-view'],
        function (DisclosureView, _, DataTableView, IFrameView, StackedTimelineView) {

            var courseModel = page.models.courseModel,
                timelineSettings = [
                    {
                        key: 'num_users',
                        title: gettext('Unique Viewers'),
                        className: 'text-right',
                        type: 'number',
                        color: 'rgb(61,162,229)'
                    },
                    {
                        key: 'num_replays',
                        title: gettext('Replays'),
                        className: 'text-right',
                        type: 'number',
                        color: 'rgb(18,46,204)'
                    }
                ],
                tableColumns = [
                    {key: 'start_time', title: gettext('Time'), type: 'time'}
                ];

            tableColumns = tableColumns.concat(timelineSettings);

            new DisclosureView({
                el: '.module-preview-disclosure'
            });

            // loading the iframe blocks content, so load it after the rest of the page loads
            new IFrameView({
                el: '#module-preview',
                loadingSelector: '#module-loading'
            });

            new StackedTimelineView({
                el: '#chart-view',
                model: courseModel,
                modelAttribute: 'videoTimeline',
                trends: timelineSettings,
                x: { key: 'start_time', title: 'Time' },
                y: { key: 'num_users' }
            });

            new DataTableView({
                el: '[data-role=data-table]',
                model: courseModel,
                modelAttribute: 'videoTimeline',
                columns: tableColumns
            });

        }
    );
});
