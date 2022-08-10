/**
 * This is the first script called by the performance answer distribution page.
 */
require('d3');
const _ = require('underscore');
const DataTableView = require('views/data-table-view');
const DiscreteBarView = require('views/stacked-bar-view');

require(['load/init-page'], (page) => {
  'use strict';

  const { courseModel } = page.models;
  const answerField = 'answer_value';
  const answerColumn = { key: answerField, title: gettext('Answer'), type: 'hasNull' };
  const tableColumns = [
    answerColumn,
    { key: 'correct', title: gettext('Correct'), type: 'bool' },
    {
      key: 'count', title: gettext('Submission Count'), type: 'number', className: 'text-right',
    },
  ];

  // answers are stored either the numeric or string fields
  if (courseModel.get('answerType') === 'numeric') {
    answerColumn.type = 'number';
  }

  // randomized problems have a random seeds field that differentiates rows
  if (courseModel.get('isRandom')) {
    // only show the variant column for randomized problems
    tableColumns.push({
      key: 'variant', title: gettext('Variant'), type: 'number', className: 'text-right',
    });
  }

  const performanceAnswerChart = new DiscreteBarView({
    el: '#performance-chart-view',
    model: courseModel,
    modelAttribute: 'answerDistributionLimited',
    dataType: 'count',
    truncateXTicks: true,
    trends: [{
      title(index) {
        if (courseModel.get('answerDistributionLimited')[index].correct) {
          return gettext('Correct');
        }
        return gettext('Incorrect');
      },
      color(answer) {
        // green bars represent bars with the correct answer
        if (answer.correct) {
          return '#4BB4FB';
        }
        return '#CA0061';
      },
    }],
    x: { key: answerField },
    y: { key: 'count' },
    // Translators: <%=value%> will be replaced by a learner response to a question asked in a course.
    interactiveTooltipHeaderTemplate: _.template(gettext('Answer: <%=value%>')),
  });
  performanceAnswerChart.renderIfDataAvailable();

  const performanceAnswerTable = new DataTableView({
    el: '[data-role=performance-table]',
    model: courseModel,
    modelAttribute: 'answerDistribution',
    columns: tableColumns,
    sorting: ['-count'],
    replaceZero: '-',
  });
  performanceAnswerTable.renderIfDataAvailable();
});
