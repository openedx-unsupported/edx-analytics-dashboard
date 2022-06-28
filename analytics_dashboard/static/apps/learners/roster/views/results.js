/**
 * Displays either a paginated table of learners or a message that there are
 * no learners to display.
 */
define((require) => {
  'use strict';

  const _ = require('underscore');
  const Marionette = require('marionette');

  const AlertView = require('components/alert/views/alert-view');
  const LearnerTableView = require('learners/roster/views/table');

  const LearnerResultsView = Marionette.LayoutView.extend({
    template: _.template('<div class="roster-main"></div>'),
    regions: {
      main: '.roster-main',
    },
    initialize(options) {
      this.options = options || {};
      this.listenTo(this.options.collection, 'sync', this.onLearnerCollectionUpdated);
    },
    onBeforeShow() {
      this.onLearnerCollectionUpdated(this.options.collection);
    },
    onLearnerCollectionUpdated(collection) {
      if (collection.length && this.options.hasData) {
        // Don't re-render the learner table view if one already exists.
        if (!(this.getRegion('main').currentView instanceof LearnerTableView)) {
          this.showChildView('main', new LearnerTableView(_.extend({
            collection,
          }, this.options)));
        }
      } else {
        this.showChildView('main', this.createAlertView(collection));
      }
    },
    createAlertView(collection) {
      const hasSearch = collection.hasActiveSearch();
      const hasActiveFilter = !_.isEmpty(collection.getActiveFilterFields());
      const suggestions = [];
      let noLearnersMessage;
      let detailedMessage;
      if (hasSearch || hasActiveFilter) {
        noLearnersMessage = gettext('No learners matched your criteria.');
        if (hasSearch) {
          suggestions.push(gettext('Try a different search.'));
        }
        if (hasActiveFilter) {
          suggestions.push(gettext('Try clearing the filters.'));
        }
      } else {
        noLearnersMessage = gettext('No learner data is currently available for your course.');
        // eslint-disable-next-line max-len
        detailedMessage = gettext('No learners are enrolled, or course activity data has not yet been processed. Data is updated every day, so check back regularly for up-to-date metrics.');
      }

      return new AlertView({
        alertType: 'info',
        title: noLearnersMessage,
        body: detailedMessage,
        suggestions,
      });
    },
  });

  return LearnerResultsView;
});
