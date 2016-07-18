/**
 * Controller object for the learners application.  Handles business
 * logic of showing different 'pages' of the application.
 *
 * Requires the following values in the options hash:
 * - learnerCollection: A `LearnerCollection` instance.
 * - rootView: A `LearnersRootView` instance.
 */
define(function(require) {
    'use strict';

    var Backbone = require('backbone'),
        Marionette = require('marionette'),
        NProgress = require('nprogress'),

        EngagementTimelineModel = require('learners/common/models/engagement-timeline'),
        LearnerDetailView = require('learners/detail/views/learner-detail'),
        LearnerModel = require('learners/common/models/learner'),
        LearnerRosterView = require('learners/roster/views/roster'),
        ReturnLinkView = require('learners/detail/views/learner-return'),

        LearnersController;

    LearnersController = Marionette.Object.extend({
        initialize: function(options) {
            this.options = options || {};
            this.listenTo(this.options.learnerCollection, 'sync', this.onLearnerCollectionUpdated);
            this.onLearnerCollectionUpdated(this.options.learnerCollection);
        },

        /**
         * Event handler for the 'showPage' event.  Called by the
         * router whenever a route method beginning with "show" has
         * been triggered.
         */
        onShowPage: function() {
            // Show a loading bar
            NProgress.done(true);
            // Clear any existing alert
            this.options.rootView.triggerMethod('clearError');
        },

        onLearnerCollectionUpdated: function(collection) {
            // Note that we currently assume that all the learners in
            // the roster were last updated at the same time.
            if (collection.length) {
                this.options.pageModel.set('lastUpdated', collection.at(0).get('last_updated'));
            }
        },

        showLearnerRosterPage: function() {
            var rosterView = new LearnerRosterView({
                collection: this.options.learnerCollection,
                courseMetadata: this.options.courseMetadata,
                trackingModel: this.options.trackingModel
            });

            this.options.rootView.getRegion('navigation').empty();

            this.options.pageModel.set('title', gettext('Learners'));
            this.onLearnerCollectionUpdated(this.options.learnerCollection);
            this.options.rootView.showChildView('main', rosterView);

            // track the "page" view
            this.options.trackingModel.set('page', 'learner_roster');
            this.options.trackingModel.trigger('segment:page');

            return rosterView;
        },

        /**
         * Render the learner detail page assuming the learner model fetch
         * succeeds.
         */
        showLearnerDetailPage: function(username) {
            var engagementTimelineModel = new EngagementTimelineModel({}, {
                    url: this.options.learnerEngagementTimelineUrl.replace('temporary_username', username),
                    courseId: this.options.courseId
                }),
                learnerModel = this.options.learnerCollection.get(username) || new LearnerModel(),
                detailView;

            this.options.rootView.showChildView('navigation', new ReturnLinkView({}));
            this.options.pageModel.set({
                title: gettext('Learner Details')
            });

            detailView = new LearnerDetailView({
                learnerModel: learnerModel,
                engagementTimelineModel: engagementTimelineModel
            });
            this.options.rootView.showChildView('main', detailView);

            // fetch data is the model is empty
            if (!learnerModel.hasData()) {
                learnerModel.on('change:last_updated', function () {
                    this.options.pageModel.set('lastUpdated', learnerModel.get('last_updated'));
                }, this);
                learnerModel.urlRoot = this.options.learnerListUrl;
                learnerModel.set({
                    course_id: this.options.courseId,
                    username: username
                })
                .fetch();
            }

            engagementTimelineModel.fetch();

            // track the "page" view
            this.options.trackingModel.set('page', 'learner_details');
            this.options.trackingModel.trigger('segment:page');

            return detailView;
        },

        showNotFoundPage: function() {
            // TODO: Implement this page in https://openedx.atlassian.net/browse/AN-6697
            var message = gettext("Sorry, we couldn't find the page you're looking for."),  // jshint ignore:line
                notFoundView;

            notFoundView = new (Backbone.View.extend({
                render: function() {
                    this.$el.text(message);
                    return this;
                }
            }))();
            this.options.rootView.showChildView('main', notFoundView);

            // track the "page" view
            this.options.trackingModel.set('page', 'learner_not_found');
            this.options.trackingModel.trigger('segment:page');
        }
    });

    return LearnersController;
});
