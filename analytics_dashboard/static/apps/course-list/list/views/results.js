/**
 * Displays either a paginated table of courses or a message that there are
 * no courses to display.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        AlertView = require('components/alert/views/alert-view'),
        CourseListTableView = require('course-list/list/views/table'),

        CourseListResultsView;

    CourseListResultsView = Marionette.LayoutView.extend({
        template: _.template('<div class="list-main"></div>'),
        regions: {
            main: '.list-main'
        },
        initialize: function(options) {
            this.options = options || {};
            this.listenTo(this.options.collection, 'backgrid:refresh', this.onCourseListCollectionUpdated);
        },
        onBeforeShow: function() {
            this.onCourseListCollectionUpdated(this.options.collection);
        },
        onCourseListCollectionUpdated: function() {
            if (this.options.collection.length && this.options.hasData) {
                // Don't re-render the courses table view if one already exists.
                if (!(this.getRegion('main').currentView instanceof CourseListTableView)) {
                    this.showChildView('main', new CourseListTableView(_.defaults({
                        collection: this.options.collection
                    }, this.options)));
                }
            } else {
                this.showChildView('main', this.createAlertView(this.options.collection));
            }
        },
        createAlertView: function(collection) {
            var hasSearch = collection.hasActiveSearch(),
                hasActiveFilter = !_.isEmpty(collection.getActiveFilterFields()),
                suggestions = [],
                noCoursesMessage,
                detailedMessage;
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
                suggestions: suggestions
            });
        }
    });

    return CourseListResultsView;
});
