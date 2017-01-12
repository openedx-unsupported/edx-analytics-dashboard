/**
 * Controller object for the course list application.  Handles business
 * logic of showing different 'pages' of the application.
 *
 * Requires the following values in the options hash:
 * - CourseListCollection: A `CourseListCollection` instance.
 * - rootView: A `CourseListRootView` instance.
 */
define(function(require) {
    'use strict';

    var $ = require('jquery'),
        Backbone = require('backbone'),
        Marionette = require('marionette'),

        CourseListView = require('course-list/list/views/course-list'),

        CourseListController;

    CourseListController = Marionette.Object.extend({
        initialize: function(options) {
            this.options = options || {};
            this.listenTo(this.options.courseListCollection, 'sync', this.onCourseListCollectionUpdated);
            this.onCourseListCollectionUpdated(this.options.courseListCollection);
        },

        /**
         * Event handler for the 'showPage' event.  Called by the
         * router whenever a route method beginning with "show" has
         * been triggered. Executes before the route method does.
         */
        onShowPage: function() {
            // Clear any existing alert
            this.options.rootView.triggerMethod('clearError');
        },

        onCourseListCollectionUpdated: function(collection) {
            // Note that we currently assume that all the courses in
            // the list were last updated at the same time.
            if (collection.length) {
                this.options.pageModel.set('lastUpdated', collection.at(0).get('last_updated'));
            }
        },

        showCourseListPage: function(queryString) {
            var listView = new CourseListView({
                    collection: this.options.courseListCollection,
                    hasData: this.options.hasData,
                    tableName: gettext('Course List'),
                    trackSubject: 'course_list',
                    appClass: 'course-list',
                    trackingModel: this.options.trackingModel
                }),
                collection = this.options.courseListCollection,
                currentPage;

            try {
                collection.setStateFromQueryString(queryString);
                this.options.rootView.showChildView('main', listView);
                if (collection.isStale) {
                    // There was a querystring sort parameter that was different from the current collection state, so
                    // we have to sort and/or search the table.

                    // We don't just do collection.fullCollection.sort() here because we've attached custom sortValue
                    // options to the columns via Backgrid to handle null values and we must call the sort function on
                    // the Backgrid table object for those custom sortValues to have an effect.
                    // Also, for some unknown reason, the Backgrid sort overwrites the currentPage, so we will save and
                    // restore the currentPage after the sort completes.
                    currentPage = collection.state.currentPage;
                    listView.getRegion('results').currentView
                            .getRegion('main').currentView.table.currentView
                            .sort(collection.state.sortKey,
                                  collection.state.order === 1 ? 'descending' : 'ascending');

                    if (collection.getSearchString() !== '') {
                        listView.getRegion('controls').currentView
                                .getRegion('search').currentView
                                .search();
                    }

                    // Not using collection.setPage() here because it appears to have a bug.
                    // This about the same as what setPage() does internally.
                    collection.getPage(currentPage - (1 - collection.state.firstPage), {reset: true});

                    collection.isStale = false;
                }
            } catch (e) {
                // These JS errors occur when trying to parse invalid URL parameters
                // FIXME: they also catch a whole lot of other kinds of errors where the alert message doesn't make much
                // sense.
                if (e instanceof RangeError || e instanceof TypeError) {
                    this.options.rootView.showAlert('error', gettext('Invalid Parameters'),
                        gettext('Sorry, we couldn\'t find any courses that matched that query.'),
                        {url: '#', text: gettext('Return to the Course List page.')});
                } else {
                    throw e;
                }
            }

            this.options.rootView.getRegion('navigation').empty();

            this.options.pageModel.set('title', gettext('Course List'));
            this.onCourseListCollectionUpdated(collection);
            collection.trigger('loaded');

            // track the "page" view
            this.options.trackingModel.set('page', {
                scope: 'insights',
                lens: 'home',
                report: '',
                depth: '',
                name: 'insights_home'
            });
            this.options.trackingModel.trigger('segment:page');

            return listView;
        },

        showNotFoundPage: function() {
            var message = gettext("Sorry, we couldn't find the page you're looking for."),
                notFoundView;

            this.options.pageModel.set('title', gettext('Page Not Found'));

            notFoundView = new (Backbone.View.extend({
                render: function() {
                    this.$el.text(message);
                    return this;
                }
            }))();
            this.options.rootView.showChildView('main', notFoundView);

            // track the "page" view
            this.options.trackingModel.set('page', {
                scope: 'insights',
                lens: 'home',
                report: 'not_found',
                depth: '',
                name: 'insights_home_not_found'
            });
            this.options.trackingModel.trigger('segment:page');
        }
    });

    return CourseListController;
});
