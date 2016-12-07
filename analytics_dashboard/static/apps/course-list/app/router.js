define(function(require) {
    'use strict';

    var Marionette = require('marionette'),

        CourseListRouter;

    CourseListRouter = Marionette.AppRouter.extend({
        // Routes intended to show a page in the app should map to method names
        // beginning with "show", e.g. 'showCourseListPage'.
        appRoutes: {
            '(/)(?*queryString)': 'showCourseListPage',
            '*notFound': 'showNotFoundPage'
        },

        // This method is run before the route methods are run.
        execute: function(callback, args, name) {
            if (name.indexOf('show') === 0) {
                this.options.controller.triggerMethod('showPage');
            }
            if (callback) {
                callback.apply(this, args);
            }
        },

        initialize: function(options) {
            this.options = options || {};
            this.courseListCollection = options.controller.options.courseListCollection;
            this.listenTo(this.courseListCollection, 'loaded', this.updateUrl);
            this.listenTo(this.courseListCollection, 'backgrid:refresh', this.updateUrl);
            Marionette.AppRouter.prototype.initialize.call(this, options);
        },

        // Called on CourseListCollection update. Converts the state of the collection (including any filters,
        // searchers, sorts, or page numbers) into a url and then navigates the router to that url.
        updateUrl: function() {
            this.navigate(this.courseListCollection.getQueryString(), {replace: true, trigger: false});
        }
    });

    return CourseListRouter;
});
