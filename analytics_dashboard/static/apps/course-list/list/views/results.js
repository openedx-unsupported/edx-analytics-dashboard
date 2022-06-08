/**
 * Displays either a paginated table of courses or a message that there are
 * no courses to display.
 */
define((require) => {
  'use strict';

  const _ = require('underscore');
  const Marionette = require('marionette');

  const AlertView = require('components/alert/views/alert-view');
  const CourseListTableView = require('course-list/list/views/table');

  const CourseListResultsView = Marionette.LayoutView.extend({
    template: _.template('<div class="list-main"></div>'),
    regions: {
      main: '.list-main',
    },
    initialize(options) {
      this.options = options || {};
      this.listenTo(this.options.collection, 'backgrid:refresh', this.onCourseListCollectionUpdated);
    },
    onBeforeShow() {
      this.onCourseListCollectionUpdated();
    },
    onCourseListCollectionUpdated() {
      if (this.options.collection.length && this.options.hasData) {
        // Don't re-render the courses table view if one already exists.
        if (!(this.getRegion('main').currentView instanceof CourseListTableView)) {
          this.showChildView('main', new CourseListTableView(_.defaults({
            collection: this.options.collection,
          }, this.options)));
        }
      } else {
        this.showChildView('main', this.createAlertView(this.options.collection));
      }
    },
    createAlertView(collection) {
      const hasSearch = collection.hasActiveSearch();
      const hasActiveFilter = !_.isEmpty(collection.getActiveFilterFields());
      const suggestions = [];
      let noCoursesMessage;
      let detailedMessage;
      if (hasSearch || hasActiveFilter) {
        noCoursesMessage = gettext('No courses matched your criteria.');
        if (hasSearch) {
          suggestions.push(gettext('Try a different search.'));
        }
        if (hasActiveFilter) {
          suggestions.push(gettext('Try clearing the filters.'));
        }
      } else {
        noCoursesMessage = gettext('No course data is currently available for your course.');
        // eslint-disable-next-line max-len
        detailedMessage = gettext('No courses are enrolled, or course activity data has not yet been processed. Data is updated every day, so check back regularly for up-to-date metrics.');
      }

      return new AlertView({
        alertType: 'info',
        title: noCoursesMessage,
        body: detailedMessage,
        suggestions,
      });
    },
  });

  return CourseListResultsView;
});
