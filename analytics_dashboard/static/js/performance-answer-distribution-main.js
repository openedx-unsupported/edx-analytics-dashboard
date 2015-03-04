/**
 * This is the first script called by the performance answer distribution page.
 */

require(['vendor/domReady!', 'load/init-page'], function(doc, page) {
    'use strict';

    require(['underscore', 'views/data-table-view', 'views/discrete-bar-view'],
            function (_, DataTableView, DiscreteBarView) {

                var courseModel = page.models.courseModel,
                    answerField = 'answer_value',
                    answerColumn = {key: answerField, title: gettext('Answer'), type:'hasNull'},
                    tableColumns = [
                        answerColumn,
                        {key: 'correct', title: gettext('Correct'), type: 'bool'},
                        {key: 'count', title: gettext('Submission Count'), type: 'number', className: 'text-right'}
                    ];

                // answers are stored either the numeric or string fields
                if (courseModel.get('answerType') === 'numeric') {
                    answerColumn.type = 'number';
                }

                // randomized problems have a random seeds field that differentiates rows
                if (courseModel.get('isRandom')) {
                    // only show the variant column for randomized problems
                    tableColumns.push({
                        key: 'variant', title: gettext('Variant'), type: 'number', className: 'text-right'
                    });
                }

                new DiscreteBarView({
                    el: '#performance-chart-view',
                    model: courseModel,
                    modelAttribute: 'answerDistributionLimited',
                    dataType: 'count',
                    truncateXTicks: true,
                    trends: [{
                        title: function(index) {
                            if (courseModel.get('answerDistributionLimited')[index].correct) {
                                return 'Correct';
                            } else {
                                return 'Incorrect';
                            }
                        },
                        color: function (bar, index) {
                            // green bars represent bars with the correct answer
                            if (courseModel.get('answerDistributionLimited')[index].correct) {
                                return '#4BB4FB';
                            } else {
                                return '#CA0061';
                            }
                        }
                    }],
                    x: { key: answerField },
                    y: { key: 'count' },
                    // Translators: <%=value%> will be replaced by a student response to a question asked in a course.
                    interactiveTooltipHeaderTemplate: _.template(gettext('Answer: <%=value%>'))
                });

                new DataTableView({
                    el: '[data-role=performance-table]',
                    model: courseModel,
                    modelAttribute: 'answerDistribution',
                    columns: tableColumns,
                    sorting: ['-count'],
                    replaceZero: '-'
                });

            });
});
