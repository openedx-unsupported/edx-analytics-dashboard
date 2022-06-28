/**
 * Controller object for the learners application.  Handles business
 * logic of showing different 'pages' of the application.
 *
 * Requires the following values in the options hash:
 * - learnerCollection: A `LearnerCollection` instance.
 * - rootView: A `LearnersRootView` instance.
 */
define((require) => {
  'use strict';

  const Backbone = require('backbone');
  const Marionette = require('marionette');
  const NProgress = require('nprogress');
  const _ = require('underscore');

  const EngagementTimelineModel = require('learners/common/models/engagement-timeline');
  const LearnerDetailView = require('learners/detail/views/learner-detail');
  const LearnerModel = require('learners/common/models/learner');
  const LearnerRosterView = require('learners/roster/views/roster');
  const LoadingView = require('components/loading/views/loading-view');
  const ReturnLinkView = require('learners/detail/views/learner-return');

  const rosterLoadingTemplate = require('components/loading/templates/plain-loading.underscore');

  const LearnersController = Marionette.Object.extend({
    initialize(options) {
      this.options = options || {};
      this.listenTo(this.options.learnerCollection, 'sync', this.onLearnerCollectionUpdated);
      this.onLearnerCollectionUpdated(this.options.learnerCollection);
    },

    /**
         * Event handler for the 'showPage' event.  Called by the
         * router whenever a route method beginning with "show" has
         * been triggered. Executes before the route method does.
         */
    onShowPage() {
      // Show a loading bar
      NProgress.done(true);
      // Clear any existing alert
      this.options.rootView.triggerMethod('clearError');
    },

    onLearnerCollectionUpdated(collection) {
      // Note that we currently assume that all the learners in
      // the roster were last updated at the same time.
      if (collection.length) {
        this.options.pageModel.set('lastUpdated', collection.at(0).get('last_updated'));
      }
    },

    showLearnerRosterPage(queryString) {
      const rosterView = new LearnerRosterView({
        collection: this.options.learnerCollection,
        courseMetadata: this.options.courseMetadata,
        tableName: gettext('Learner Roster'),
        trackSubject: 'roster',
        appClass: 'learners',
        hasData: this.options.hasData,
        trackingModel: this.options.trackingModel,
      });
      const loadingView = new LoadingView({
        model: this.options.learnerCollection,
        template: _.template(rosterLoadingTemplate),
        successView: rosterView,
      });
      let fetch;

      try {
        this.options.learnerCollection.setStateFromQueryString(queryString);
        if (this.options.learnerCollection.isStale) {
          // Show a loading spinner while we fetch new collection data
          this.options.rootView.showChildView('main', loadingView);

          fetch = this.options.learnerCollection.fetch({ reset: true });
          if (fetch) {
            fetch.complete(response => {
              // fetch doesn't empty the collection on 404 by default
              if (response && response.status === 404) {
                this.options.learnerCollection.reset();
              }
            });
          }
        } else {
          // Immediately show the roster with the currently loaded collection data
          this.options.rootView.showChildView('main', rosterView);
        }
      } catch (e) {
        // These JS errors occur when trying to parse invalid URL parameters
        if (e instanceof RangeError || e instanceof TypeError) {
          this.options.rootView.showAlert(
            'error',
            gettext('Invalid Parameters'),
            gettext('Sorry, we couldn\'t find any learners who matched that query.'),
            { url: '#', text: gettext('Return to the Learners page.') },
          );
        } else {
          throw e;
        }
      }

      this.options.rootView.getRegion('navigation').empty();

      this.options.pageModel.set('title', gettext('Learners'));
      this.onLearnerCollectionUpdated(this.options.learnerCollection);

      // track the "page" view
      this.options.trackingModel.set('page', {
        scope: 'course',
        lens: 'learners',
        report: 'roster',
        depth: '',
        name: 'course_learners_details',
      });
      this.options.trackingModel.trigger('segment:page');

      return rosterView;
    },

    /**
         * Render the learner detail page assuming the learner model fetch
         * succeeds.
         */
    showLearnerDetailPage(username) {
      const engagementTimelineModel = new EngagementTimelineModel({}, {
        url: this.options.learnerEngagementTimelineUrl.replace('temporary_username', username),
        courseId: this.options.courseId,
      });
      const learnerModel = this.options.learnerCollection.get(username) || new LearnerModel();

      this.options.rootView.showChildView('navigation', new ReturnLinkView({
        queryString: this.options.learnerCollection.getQueryString(),
      }));

      this.options.pageModel.set({
        title: gettext('Learner Details'),
      });

      const detailView = new LearnerDetailView({
        learnerModel,
        engagementTimelineModel,
        trackingModel: this.options.trackingModel,
      });
      this.options.rootView.showChildView('main', detailView);

      // fetch data is the model is empty
      if (!learnerModel.hasData()) {
        learnerModel.on('change:last_updated', () => {
          this.options.pageModel.set('lastUpdated', learnerModel.get('last_updated'));
        }, this);
        learnerModel.urlRoot = this.options.learnerListUrl;
        learnerModel.set({
          course_id: this.options.courseId,
          username,
        })
          .fetch();
      }

      engagementTimelineModel.fetch();

      // track the "page" view
      this.options.trackingModel.set('page', {
        scope: 'course',
        lens: 'learners',
        report: 'details',
        depth: '',
        name: 'course_learners_details',
      });
      this.options.trackingModel.trigger('segment:page');

      return detailView;
    },

    showNotFoundPage() {
      // TODO: Implement this page in https://openedx.atlassian.net/browse/AN-6697
      const message = gettext("Sorry, we couldn't find the page you're looking for.");

      this.options.pageModel.set('title', gettext('Page Not Found'));

      const notFoundView = new (Backbone.View.extend({
        render() {
          this.$el.text(message);
          return this;
        },
      }))();
      this.options.rootView.showChildView('main', notFoundView);

      // track the "page" view
      this.options.trackingModel.set('page', {
        scope: 'course',
        lens: 'learners',
        report: 'learner_not_found',
        depth: '',
        name: 'course_learners_learner_not_found',
      });
      this.options.trackingModel.trigger('segment:page');
    },
  });

  return LearnersController;
});
