define(function(require) {
    'use strict';

    var $ = require('jquery'),
        Backbone = require('backbone'),
        Marionette = require('marionette'),
        _ = require('underscore'),

        initModels = require('load/init-page'),

        CourseListCollection = require('course-list/common/collections/course-list'),
        CourseListController = require('course-list/app/controller'),
        RootView = require('components/root/views/root'),
        CourseListRouter = require('course-list/app/router'),
        PageModel = require('components/generic-list/common/models/page'),
        SkipLinkView = require('components/skip-link/views/skip-link-view'),

        CourseListApp;

    CourseListApp = Marionette.Application.extend({
        /**
         * Initializes the course-list analytics app.
         */
        initialize: function(options) {
            this.options = options || {};
        },

        onStart: function() {
            var pageModel = new PageModel(),
                courseListCollection,
                rootView;

            new SkipLinkView({
                el: 'body'
            }).render();

            courseListCollection = new CourseListCollection(this.options.courseListJson, {
                downloadUrl: this.options.courseListDownloadUrl,
                mode: 'client'
            });

            rootView = new RootView({
                el: $(this.options.containerSelector),
                pageModel: pageModel,
                appClass: 'course-list',
                displayHeader: false
            }).render();

            new CourseListRouter({ // eslint-disable-line no-new
                controller: new CourseListController({
                    courseListCollection: courseListCollection,
                    hasData: _.isObject(this.options.courseListJson),
                    pageModel: pageModel,
                    rootView: rootView,
                    trackingModel: initModels.models.trackingModel
                })
            });

            Backbone.history.start();
        }
    });

    return CourseListApp;
});
