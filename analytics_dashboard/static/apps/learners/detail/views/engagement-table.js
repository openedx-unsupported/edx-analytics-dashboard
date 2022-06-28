define((require) => {
  'use strict';

  const _ = require('underscore');
  const Marionette = require('marionette');
  const DataTableView = require('views/data-table-view');

  const LearnerEngagementTableView = Marionette.LayoutView.extend({
    template: _.template(require('learners/detail/templates/engagement-table.underscore')),
    regions: {
      main: '.learner-engagement-table.analytics-table',
    },
    onAttach() {
      const learnerEngagementTable = new DataTableView({
        el: this.regions.main,
        model: this.model,
        modelAttribute: 'days',
        columns: [
          {
            key: 'date',
            title: gettext('Date'),
            type: 'date',
          },
          {
            key: 'discussion_contributions',
            title: gettext('Discussion Contributions'),
            className: 'text-right',
            type: 'number',
          },
          {
            key: 'problems_completed',
            title: gettext('Problems Correct'),
            className: 'text-right',
            type: 'number',
          },
          {
            key: 'videos_viewed',
            title: gettext('Videos Viewed'),
            className: 'text-right',
            type: 'number',
          },
        ],
        sorting: ['-date'],
        replaceNull: '-',
      });
      learnerEngagementTable.renderIfDataAvailable();
    },
  });

  return LearnerEngagementTableView;
});
