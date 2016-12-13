define(function(require) {
    'use strict';

    var $ = require('jquery'),
        Backbone = require('backbone'),
        Marionette = require('marionette'),
        NProgress = require('nprogress'),
        _ = require('underscore'),

        initModels = require('load/init-page'),

        CourseListCollection = require('course-list/common/collections/course-list'),
        CourseListController = require('course-list/app/controller'),
        CourseListRootView = require('course-list/app/views/root'),
        CourseListRouter = require('course-list/app/router'),
        PageModel = require('generic-list/common/models/page'),

        CourseListApp;

    CourseListApp = Marionette.Application.extend({
        /**
         * Initializes the course-list analytics app.
         *
         * @param options specifies the following values:
         * TODO: complete.
         */
        initialize: function(options) {
            this.options = options || {};
        },

        onStart: function() {
            var pageModel = new PageModel(),
                courseListCollection,
                rootView;

            courseListCollection = new CourseListCollection(this.options.courseListJson, {
                url: this.options.courseListUrl,
                downloadUrl: this.options.courseListDownloadUrl,
                mode: 'client'
            });

            rootView = new CourseListRootView({
                el: $(this.options.containerSelector),
                pageModel: pageModel
            }).render();

            new CourseListRouter({ // eslint-disable-line no-new
                controller: new CourseListController({
                    courseListCollection: courseListCollection,
                    hasData: _.isObject(this.options.courseListJson),
                    pageModel: pageModel,
                    rootView: rootView,
                    courseListUrl: this.options.courseListUrl,
                    trackingModel: initModels.models.trackingModel
                })
            });

            // If we haven't been provided with any data, fetch it now
            // from the server.
            if (!this.options.courseListJson) {
                courseListCollection.setPage(1);
            }

            Backbone.history.start();

            // Loading progress bar via nprogress
            NProgress.configure({showSpinner: false});
            $(document).ajaxStart(function() { NProgress.start(); });
            $(document).ajaxStop(function() { NProgress.done(); });
        }
    });

    return CourseListApp;
});
