define(function(require) {
    'use strict';

    var $ = require('jquery'),
        Backbone = require('backbone'),
        Marionette = require('marionette'),
        NProgress = require('nprogress'),
        _ = require('underscore'),

        initModels = require('load/init-page'),

        CourseMetadataModel = require('learners/common/models/course-metadata'),
        LearnerCollection = require('learners/common/collections/learners'),
        LearnersController = require('learners/app/controller'),
        LearnersRootView = require('components/root/views/root'),
        LearnersRouter = require('learners/app/router'),
        PageModel = require('components/generic-list/common/models/page'),
        SkipLinkView = require('components/skip-link/views/skip-link-view'),

        LearnersApp;

    LearnersApp = Marionette.Application.extend({
        /**
         * Initializes the learner analytics app.
         *
         * @param options specifies the following values:
         * - courseId (string) required - the course id for this
         *   learner app.
         * - containerSelector (string) required - the CSS selector
         *   for the HTML element that this app should attach to
         * - learnerListUrl (string) required - the URL for the
         *   Learner List API endpoint.
         * - learnerListDownloadUrl (string) required - the CSV download URL
         *   for the Learner List API endpoint.
         * - courseLearnerMetadataUrl (String) required - the URL for
         *   the Course Learner Metadata API endpoint.
         * - learnerListJson (Object) optional - an Object
         *   representing an initial server response from the Learner
         *   List endpoint used for pre-populating the app's
         *   LearnerCollection.  If not provided, the data is fetched
         *   asynchronously before app initialization.
         * - courseLearnerMetadataJson (Object) optional - an Object
         *   representing an initial server response from the Learner
         *   Course Metadata endpoint used for data on cohorts,
         *   segments, enrollment modes, and engagement ranges.
         * - learnerEngagementTimelineUrl (String) required - the URL for the
         *   Learner Engagement Timeline API endpoint.
         */
        initialize: function(options) {
            this.options = options || {};
        },

        onStart: function() {
            var pageModel = new PageModel(),
                courseMetadata,
                learnerCollection,
                rootView;

            new SkipLinkView({
                el: 'body'
            }).render();

            learnerCollection = new LearnerCollection(this.options.learnerListJson, {
                url: this.options.learnerListUrl,
                downloadUrl: this.options.learnerListDownloadUrl,
                courseId: this.options.courseId,
                parse: this.options.learnerListJson
            });

            courseMetadata = new CourseMetadataModel(this.options.courseLearnerMetadataJson, {
                url: this.options.courseLearnerMetadataUrl,
                parse: true
            });

            rootView = new LearnersRootView({
                el: $(this.options.containerSelector),
                pageModel: pageModel,
                appClass: 'learners'
            }).render();

            new LearnersRouter({ // eslint-disable-line no-new
                controller: new LearnersController({
                    courseId: this.options.courseId,
                    learnerCollection: learnerCollection,
                    courseMetadata: courseMetadata,
                    hasData: _.isObject(this.options.learnerListJson),
                    pageModel: pageModel,
                    rootView: rootView,
                    learnerEngagementTimelineUrl: this.options.learnerEngagementTimelineUrl,
                    learnerListUrl: this.options.learnerListUrl,
                    trackingModel: initModels.models.trackingModel
                })
            });

            // If we haven't been provided with any data, fetch it now
            // from the server.
            if (!this.options.learnerListJson) {
                learnerCollection.setPage(1);
            }
            if (!this.options.courseLearnerMetadataJson) {
                courseMetadata.fetch();
            }

            Backbone.history.start();

            // Loading progress bar via nprogress
            NProgress.configure({showSpinner: false});
            $(document).ajaxStart(function() { NProgress.start(); });
            $(document).ajaxStop(function() { NProgress.done(); });
        }
    });

    return LearnersApp;
});
