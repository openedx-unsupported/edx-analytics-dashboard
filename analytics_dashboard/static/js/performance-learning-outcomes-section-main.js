require(['load/init-page'], (page) => {
  'use strict';

  require(
    ['d3', 'underscore', 'views/data-table-view', 'views/stacked-bar-view'],
    (d3, _, DataTableView, StackedBarView) => {
      const model = page.models.courseModel;
      const graphSubmissionColumns = [
        {
          key: 'correct_submissions',
          percent_key: 'correct_percent',
          title: gettext('Correct'),
          className: 'text-right',
          type: 'number',
          fractionDigits: 1,
          color: '#4BB4FB',
        },
        {
          key: 'incorrect_submissions',
          percent_key: 'incorrect_percent',
          title: gettext('Incorrect'),
          className: 'text-right',
          type: 'number',
          fractionDigits: 1,
          color: '#CA0061',
        },
      ];
      const tableColumns = [
        {
          key: 'index', title: gettext('Order'), type: 'number', className: 'text-right',
        },
        { key: 'name', title: model.get('contentTableHeading'), type: 'hasNull' },
        { key: 'difficulty', title: gettext('Difficulty'), type: 'hasNull' },
      ];
      let performanceLoSectionChart;
      let performanceLoSectionTable;

      tableColumns.push({
        key: 'correct_submissions',
        title: gettext('Correct'),
        className: 'text-right',
        type: 'number',
        fractionDigits: 1,
      });

      tableColumns.push({
        key: 'incorrect_submissions',
        title: gettext('Incorrect'),
        className: 'text-right',
        type: 'number',
        fractionDigits: 1,
      });

      tableColumns.push({
        key: 'total_submissions',
        title: gettext('Total'),
        className: 'text-right',
        type: 'number',
        fractionDigits: 1,
      });

      tableColumns.push({
        key: 'correct_percent',
        title: gettext('Percentage Correct'),
        className: 'text-right',
        type: 'percent',
      });

      if (model.get('hasData')) {
        performanceLoSectionChart = new StackedBarView({
          el: '#chart-view',
          model,
          modelAttribute: 'tagsDistribution',
          trends: graphSubmissionColumns,
        });
        performanceLoSectionChart.renderIfDataAvailable();
      }

      performanceLoSectionTable = new DataTableView({
        el: '[data-role=data-table]',
        model,
        modelAttribute: 'tagsDistribution',
        columns: tableColumns,
        sorting: ['index'],
        replaceZero: '-',
      });
      performanceLoSectionTable.renderIfDataAvailable();
    },
  );
});
