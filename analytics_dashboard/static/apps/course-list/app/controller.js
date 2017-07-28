/**
 * Controller object for the course list application.  Handles business
 * logic of showing different 'pages' of the application.
 *
 * Requires the following values in the options hash:
 * - CourseListCollection: A `CourseListCollection` instance.
 * - rootView: A `CourseListRootView` instance.
 */
import _ from 'underscore';
import Backbone from 'backbone';
import Marionette from 'marionette';
import NProgress from 'nprogress';

import CourseListView from 'course-list/list/views/course-list';
import LoadingTemplate from 'components/loading/templates/plain-loading.underscore';
import LoadingView from 'components/loading/views/loading-view';

export default class CourseListController extends Marionette.Object {
  constructor(options) {
    super();
    this.options = options || {};
    this.listenTo(this.options.courseListCollection, 'sync', this.onCourseListCollectionUpdated);
    this.listenTo(this.options.courseListCollection, 'error', this.showError);
    this.onCourseListCollectionUpdated(this.options.courseListCollection);
  }

  /**
     * Event handler for the 'showPage' event.  Called by the
     * router whenever a route method beginning with "show" has
     * been triggered. Executes before the route method does.
     */
  onShowPage() {
    // clear loading bar
    NProgress.done(true);
    // Clear any existing alert
    this.options.rootView.triggerMethod('clearError');
  }

  onCourseListCollectionUpdated(collection) {
    // Note that we currently assume that all the courses in
    // the list were last updated at the same time.
    if (collection.length) {
      this.options.pageModel.set('lastUpdated', collection.at(0).get('last_updated'));
    }
    this.options.rootView.triggerMethod('clearError');
  }

  showCourseListPage(queryString) {
    const listView = new CourseListView({
      collection: this.options.courseListCollection,
      hasData: this.options.hasData,
      tableName: gettext('Course List'),
      trackSubject: 'course_list',
      appClass: 'course-list',
      trackingModel: this.options.trackingModel,
      filteringEnabled: this.options.filteringEnabled,
    });

    const collection = this.options.courseListCollection;

    try {
      collection.setStateFromQueryString(queryString);
      if (collection.isStale || collection.getResultCount() === 0) {
        const loadingView = new LoadingView({
          model: collection,
          template: _.template(LoadingTemplate),
          successView: listView,
        });
        this.options.rootView.showChildView('main', loadingView);

        const fetch = collection.fetch({ reset: true });
        if (fetch) {
          fetch.complete((response) => {
            if (response && response.status === 404) {
              collection.reset();
            }
          });
        }
      } else {
        this.options.rootView.showChildView('main', listView);
      }
    } catch (e) {
      // These JS errors occur when trying to parse invalid URL parameters
      // FIXME: they also catch a whole lot of other kinds of errors where the alert message doesn't
      // make much sense
      if (e instanceof RangeError || e instanceof TypeError) {
        this.options.rootView.showAlert(
          'error',
          gettext('Invalid Parameters'),
          gettext("Sorry, we couldn't find any courses that matched that query."),
          { url: '#', text: gettext('Return to the Course List page.') },
        );
      } else {
        throw e;
      }
    }

    this.options.rootView.getRegion('navigation').empty();

    this.options.pageModel.set('title', gettext('Course List'));
    collection.trigger('loaded');

    // track the "page" view
    this.options.trackingModel.set('page', {
      scope: 'insights',
      lens: 'home',
      report: '',
      depth: '',
      name: 'insights_home',
    });
    this.options.trackingModel.trigger('segment:page');

    return listView;
  }

  showNotFoundPage() {
    const message = gettext("Sorry, we couldn't find the page you're looking for.");

    this.options.pageModel.set('title', gettext('Page Not Found'));

    const notFoundView = new (Backbone.View.extend({
      render() {
        this.$el.text(message);
        return this;
      },
    }))();
    this.options.rootView.showChildView('main', notFoundView);

    // track the "page" view
    this.options.trackingModel.set('page', {
      scope: 'insights',
      lens: 'home',
      report: 'not_found',
      depth: '',
      name: 'insights_home_not_found',
    });
    this.options.trackingModel.trigger('segment:page');
  }

  showError() {
    this.options.rootView.showAlert(
      'error',
      gettext('Server error'),
      gettext('Your request could not be processed. Reload the page to try again.')
    );
  }

}
