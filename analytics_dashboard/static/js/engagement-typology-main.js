/**
 * This is the first script called by the engagement page.  It loads
 * the libraries and kicks off the application.
 */

require(['vendor/domReady!', 'load/init-page'], function (doc, page) {
    'use strict';

    require(['d3', 'underscore', 'views/data-table-view', 'views/stacked-bar-view'],
        function (d3, _, DataTableView, StackedBarView) {
            var model = page.models.courseModel,
                graphSubmissionColumns = [
                    {
                        key: 'all_v_all_p',  // All Videos, All Problems
                        title: gettext('All Videos, All Problems'),
                        shortTitle: '▸▸&nbsp;■■',
                        color: 'hsl(113, 5%, 10%)' // H 113, S 5 for students w/ same vid & problem type
                    },
                    {
                        key: 'all_v_some_p',  // All Videos, Some Problems
                        title: gettext('All Videos, Some Problems'),
                        shortTitle: '▸▸&nbsp;■□',
                        color: 'hsl(200, 75%, 25%)' // H 200, S 75 for students w/ more video than problems
                    },
                    {
                        key: 'some_v_all_p',  // Some Videos, All Problems
                        title: gettext('Some Videos, All Problems'),
                        shortTitle: '▸▹&nbsp;■■',
                        color: 'hsl(62, 85%, 25%)' // H 62, S 85 for students w/ more problem than video
                    },
                    {
                        key: 'all_v_no_p',  // All Videos, No Problems
                        title: gettext('All Videos, No Problems'),
                        shortTitle: '▸▸&nbsp;□□',
                        color: 'hsl(200, 75%, 35%)' // H 200, S 75 for students w/ more video than problems
                    },
                    {
                        key: 'no_v_all_p',  // No Videos, All Problems
                        title: gettext('No Videos, All Problems'),
                        shortTitle: '▹▹&nbsp;■■',
                        color: 'hsl(62, 85%, 35%)' // H 62, S 85 for students w/ more problem than video
                    },
                    {
                        key: 'some_v_some_p',  // Some Videos, Some Problems
                        title: gettext('Some Videos, Some Problems'),
                        shortTitle: '▸▹&nbsp;■□',
                        color: 'hsl(113, 5%, 50%)' // H 113, S 5 for students w/ same vid & problem type
                    },
                    {
                        key: 'some_v_no_p',  // Some Videos, No Problems
                        title: gettext('Some Videos, No Problems'),
                        shortTitle: '▸▹&nbsp;□□',
                        className: 'text-right',
                        type: 'number',
                        color: 'hsl(200, 75%, 75%)' // H 200, S 75 for students w/ more video than problems
                    },
                    {
                        key: 'no_v_some_p',  // No Videos, Some Problems
                        title: gettext('No Videos, Some Problems'),
                        shortTitle: '▹▹&nbsp;■□',
                        className: 'text-right',
                        type: 'number',
                        color: 'hsl(62, 85%, 75%)' // H 62, S 85 for students w/ more problem than video
                    }
                ],
                tableColumns = [
                    {key: 'index', title: gettext('Chapter'), type: 'custom', displayKey: 'name'}
                ];

            _(graphSubmissionColumns).each(function(col) {
                col.percent_key = col.key + '_fraction';
                col.shortTitle = '<span title="' + col.title + '" class=symbolic-header>' + col.shortTitle + '</span>';
                col.title += ' (' + col.shortTitle + ')';
                col.type = 'number';
                var newCol = _.clone(col);
                newCol.title = col.shortTitle;
                newCol.className = 'text-right';
                newCol.unorderable = true;
                tableColumns.push(newCol);
            });

            new StackedBarView({
                el: '#chart-view',
                model: model,
                modelAttribute: 'typology',
                trends: graphSubmissionColumns,
                showAllSeriesInTooltip: false,
                x: {key: 'index', displayKey: 'name'}
            });

            new DataTableView({
                el: '[data-role=data-table]',
                model: model,
                modelAttribute: 'typology',
                columns: tableColumns,
                sorting: ['index'],
                replaceZero: '-'
            });
        }
    );
});
