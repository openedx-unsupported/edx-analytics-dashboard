/**
 * Controller object for the learners application.  Handles business
 * logic of showing different 'pages' of the application.
 *
 * Requires the following values in the options hash:
 * - learnerCollection: A `LearnerCollection` instance.
 * - rootView: A `LearnersRootView` instance.
 */
define([
    'backbone',
    'marionette',
    'learners/js/models/engagement-timeline',
    'learners/js/views/learner-detail',
    'learners/js/views/roster-view'
], function (
    Backbone,
    Marionette,
    EngagementTimelineModel,
    LearnerDetailView,
    LearnerRosterView
) {
    'use strict';

    var LearnersController = Marionette.Object.extend({
        initialize: function (options) {
            this.options = options || {};
        },

        showLearnerRosterPage: function () {
            this.options.rootView.showChildView('main', new LearnerRosterView({
                collection: this.options.learnerCollection,
                courseMetadata: this.options.courseMetadata
            }));
        },

        /**
         * Render the learner detail page assuming the learner model fetch
         * succeeds.
         *
         * @returns a jqXHR representing the learner engagement model fetch.
         */
        showLearnerDetailPage: function (username) {
            var engagementTimelineModel = new EngagementTimelineModel({}, {
                url: this.options.learnerEngagementTimelineUrl.replace('temporary_username', username),
                courseId: this.options.courseId
            });
            this.options.rootView.showChildView('main', new LearnerDetailView({
                engagementTimelineModel: engagementTimelineModel
            }));
            return engagementTimelineModel.fetch();
        },

        showNotFoundPage: function () {
            // TODO: Implement this page in https://openedx.atlassian.net/browse/AN-6697
            var message = gettext("Sorry, we couldn't find the page you're looking for.");  // jshint ignore:line
            this.options.rootView.showChildView('main', new (Backbone.View.extend({
                render: function () {this.$el.text(message); return this;}
            }))());
        }
    });

    return LearnersController;
});
