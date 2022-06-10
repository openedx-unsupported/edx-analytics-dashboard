/**
 * This is the first script called by the enrollment demographics education page.  It loads
 * the libraries and kicks off the application.
 */
import { template } from 'underscore';
import DataTableView from 'views/data-table-view';
import DiscreteBarView from 'views/discrete-bar-view';
import page from 'load/init-page';

define(() => {
  'use strict';

  const educationChart = new DiscreteBarView({
    el: '#enrollment-chart-view',
    model: page.models.courseModel,
    modelAttribute: 'education',
    excludeData: ['Unknown'],
    dataType: 'percent',
    trends: [{
      title: gettext('Percentage'),
      color: 'rgb(58, 162, 224)',
    }],
    x: { key: 'educationLevel' },
    y: { key: 'percent' },
    // Translators: <%=value%> will be replaced with a level of education (e.g. Doctorate).
    interactiveTooltipHeaderTemplate: template(gettext('Education: <%=value%>')),
  });
  const educationTable = new DataTableView({
    el: '[data-role=enrollment-table]',
    model: page.models.courseModel,
    modelAttribute: 'education',
    columns: [
      { key: 'educationLevel', title: gettext('Educational Background') },
      {
        key: 'count', title: gettext('Number of Learners'), type: 'number', className: 'text-right',
      },
    ],
    sorting: ['-count'],
  });

  educationChart.renderIfDataAvailable();
  educationTable.renderIfDataAvailable();
});
