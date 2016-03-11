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
    'learners/js/views/roster-view'
], function (Backbone, Marionette, LearnerRosterView) {
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

        showLearnerDetailPage: function (username) {
            // TODO: we'll eventually have to fetch the learner either
            // from the cached collection, or from the server.  See
            // https://openedx.atlassian.net/browse/AN-6191
            this.options.rootView.showChildView('main', new (Backbone.View.extend({
                render: function () {this.$el.text(username); return this;}
            }))());
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
