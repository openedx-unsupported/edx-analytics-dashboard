define([
    'backbone',
    'jquery',
    'learners/js/collections/learner-collection',
    'learners/js/controller',
    'learners/js/models/course-metadata',
    'learners/js/router',
    'learners/js/views/root-view',
    'marionette',
    'underscore'
], function (
    Backbone,
    $,
    LearnerCollection,
    LearnersController,
    CourseMetadataModel,
    LearnersRouter,
    LearnersRootView,
    Marionette,
    _
) {
    'use strict';

    var LearnersApp;

    LearnersApp = Marionette.Application.extend({
        /**
         * Initializes the learner analytics app.
         *
         * @param options specifies the following values:
         * - courseId (string) required - the course id for this
         *   learner app
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
                    learnerCollection: learnerCollection,
                    courseMetadata: courseMetadata,
                    rootView: rootView
                })
            });

            // If we haven't been provided with any data, fetch it now
            // from the server.
            if (!this.options.learnerListJson || _.isEmpty(this.options.learnerListJson)) {
                learnerCollection.setPage(1); // Returns deferred.promise()
            }
            if (!this.options.courseLearnerMetadataJson || _.isEmpty(this.options.courseLearnerMetadataJson)) {
                courseMetadata.fetch(); // Returns a jqXHR
            }
            // If the above requests fail, don't render the learner
            // roster page.

            Backbone.history.start();
        }
    });

    return LearnersApp;
});
