import Marionette from 'marionette';

class CourseListRouter extends Marionette.AppRouter {
  // Routes intended to show a page in the app should map to method names
  // beginning with "show", e.g. 'showCourseListPage'.
  constructor(options) {
    super(options);
    this.options = options || {};
    this.courseListCollection = options.controller.options.courseListCollection;
    this.listenTo(this.courseListCollection, 'loaded', this.updateUrl);
    this.listenTo(this.courseListCollection, 'backgrid:refresh', this.updateUrl);
    // Marionette.AppRouter.prototype.initialize.call(this, options);
  }

  // This method is run before the route methods are run.
  execute(callback, args, name) {
    if (name.indexOf('show') === 0) {
      this.options.controller.triggerMethod('showPage');
    }
    if (callback) {
      callback.apply(this, args);
    }
  }

  // Called on CourseListCollection update. Converts the state of the collection (including any
  // filters, searchers, sorts, or page numbers) into a url and then navigates the router to that
  // url.
  updateUrl() {
    this.navigate(this.courseListCollection.getQueryString(), {
      replace: true,
      trigger: false,
    });
  }
}

CourseListRouter.prototype.appRoutes = {
  '(/)(?*queryString)': 'showCourseListPage',
  '*notFound': 'showNotFoundPage',
};

export default CourseListRouter;
