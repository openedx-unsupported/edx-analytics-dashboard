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

    var Backbone = require('backbone'),
        Marionette = require('marionette'),
        NProgress = require('nprogress'),

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
            // Show a loading bar
            NProgress.done(true);
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
                trackingModel: this.options.trackingModel
            });

            try {
                this.options.courseListCollection.setStateFromQueryString(queryString);
                this.options.rootView.showChildView('main', listView);
            } catch (e) {
                // These JS errors occur when trying to parse invalid URL parameters
                if (e instanceof RangeError || e instanceof TypeError) {
                    this.options.rootView.showAlert('error', gettext('Invalid Parameters'),
                        gettext('Sorry, we couldn\'t find any courses that matched that query.'),
                        {url: '#', text: gettext('Return to the Course List page.')});
                    console.error(e);
                } else {
                    throw e;
                }
            }

            this.options.rootView.getRegion('navigation').empty();

            this.options.pageModel.set('title', gettext('Course List'));
            this.onCourseListCollectionUpdated(this.options.courseListCollection);
            this.options.courseListCollection.trigger('loaded');

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
            // TODO: Implement this page in https://openedx.atlassian.net/browse/AN-6697
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
