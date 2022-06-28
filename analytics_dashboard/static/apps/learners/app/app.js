define((require) => {
  'use strict';

  const $ = require('jquery');
  const Backbone = require('backbone');
  const Marionette = require('marionette');
  const NProgress = require('nprogress');
  const _ = require('underscore');

  const initModels = require('load/init-page');

  const CourseMetadataModel = require('learners/common/models/course-metadata');
  const LearnerCollection = require('learners/common/collections/learners');
  const LearnersController = require('learners/app/controller');
  const LearnersRootView = require('components/root/views/root');
  const LearnersRouter = require('learners/app/router');
  const PageModel = require('components/generic-list/common/models/page');
  const SkipLinkView = require('components/skip-link/views/skip-link-view');

  const LearnersApp = Marionette.Application.extend({
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
    initialize(options) {
      this.options = options || {};
    },

    onStart() {
      const pageModel = new PageModel();

      new SkipLinkView({
        el: 'body',
      }).render();

      const learnerCollection = new LearnerCollection(this.options.learnerListJson, {
        url: this.options.learnerListUrl,
        downloadUrl: this.options.learnerListDownloadUrl,
        courseId: this.options.courseId,
        parse: this.options.learnerListJson,
      });

      const courseMetadata = new CourseMetadataModel(this.options.courseLearnerMetadataJson, {
        url: this.options.courseLearnerMetadataUrl,
        parse: true,
      });

      const rootView = new LearnersRootView({
        el: $(this.options.containerSelector),
        pageModel,
        appClass: 'learners',
      }).render();

      new LearnersRouter({ // eslint-disable-line no-new
        controller: new LearnersController({
          courseId: this.options.courseId,
          learnerCollection,
          courseMetadata,
          hasData: _.isObject(this.options.learnerListJson),
          pageModel,
          rootView,
          learnerEngagementTimelineUrl: this.options.learnerEngagementTimelineUrl,
          learnerListUrl: this.options.learnerListUrl,
          trackingModel: initModels.models.trackingModel,
        }),
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
      NProgress.configure({ showSpinner: false });
      $(document).ajaxStart(() => { NProgress.start(); });
      $(document).ajaxStop(() => { NProgress.done(); });
    },
  });

  return LearnersApp;
});
