define([
    'backbone',
    'jquery',
    'learners/js/collections/learner-collection',
    'learners/js/controller',
    'learners/js/models/course-metadata',
    'learners/js/router',
    'learners/js/views/root-view',
    'marionette'
], function (
    Backbone,
    $,
    LearnerCollection,
    LearnersController,
    CourseMetadataModel,
    LearnersRouter,
    LearnersRootView,
    Marionette
) {
    'use strict';

    var LearnersApp;

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
        initialize: function (options) {
            this.options = options || {};
        },

        onStart: function () {
            var courseMetadata,
                learnerCollection,
                rootView,
                router;

            learnerCollection = new LearnerCollection(this.options.learnerListJson, {
                url: this.options.learnerListUrl,
                courseId: this.options.courseId,
                parse: this.options.learnerListJson ? true : false
            });

            courseMetadata = new CourseMetadataModel(this.options.courseLearnerMetadataJson, {
                url: this.options.courseLearnerMetadataUrl,
                parse: true
            });

            rootView = new LearnersRootView({el: $(this.options.containerSelector)}).render();

            router = new LearnersRouter({
                controller: new LearnersController({
                    courseId: this.options.courseId,
                    learnerCollection: learnerCollection,
                    courseMetadata: courseMetadata,
                    rootView: rootView,
                    learnerEngagementTimelineUrl: this.options.learnerEngagementTimelineUrl
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
        }
    });

    return LearnersApp;
});
