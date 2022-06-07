define((require) => {
  'use strict';

  const _ = require('underscore');
  const Marionette = require('marionette');

  const ListUtils = require('components/utils/utils');
  const Utils = require('utils/utils');

  const AlertView = require('components/alert/views/alert-view');
  const LearnerEngagementTableView = require('learners/detail/views/engagement-table');
  const LearnerEngagementTimelineView = require('learners/detail/views/engagement-timeline');
  const LearnerNameView = require('learners/detail/views/learner-names');
  const LearnerSummaryFieldView = require('learners/detail/views/learner-summary-field');
  const LoadingView = require('components/loading/views/loading-view');
  const chartLoadingTemplate = require('components/loading/templates/chart-loading.underscore');
  const tableLoadingTemplate = require('components/loading/templates/table-loading.underscore');
  const learnerDetailTemplate = require('learners/detail/templates/learner-detail.underscore');

  return Marionette.LayoutView.extend({
    className: 'learner-detail-container',

    template: _.template(learnerDetailTemplate),

    templateHelpers() {
      return {
        // Translators: e.g. Learner engagement activity
        engagement: gettext('Engagement Activity'),
        activity: gettext('Daily Activity'),
        table: gettext('Activity Over Time'),
      };
    },

    regions: {
      learnerSummary: '.learner-summary-container',
      names: '.learner-names',
      enrollment: '.learner-enrollment',
      cohort: '.learner-cohort',
      accessed: '.learner-accessed',
      engagementTimeline: '.learner-engagement-timeline-container',
      engagementTable: '.learner-engagement-table-container',
    },

    initialize(options) {
      Marionette.LayoutView.prototype.initialize.call(this, options);
      this.options = options || {};
      ListUtils.mapEvents(this.options.engagementTimelineModel, {
        serverError: this.timelineServerErrorToAppError,
        networkError: ListUtils.EventTransformers.networkErrorToAppError,
        sync: ListUtils.EventTransformers.syncToClearError,
      }, this);
      this.listenTo(this, 'engagementTimelineUnavailable', this.showTimelineUnavailable);

      ListUtils.mapEvents(this.options.learnerModel, {
        serverError: this.learnerServerErrorToAppError,
        networkError: ListUtils.EventTransformers.networkErrorToAppError,
        sync: ListUtils.EventTransformers.syncToClearError,
      }, this);
      this.listenTo(this, 'learnerUnavailable', this.showLearnerUnavailable);
    },

    onBeforeShow() {
      const { learnerModel } = this.options;
      const timelineModel = this.options.engagementTimelineModel;
      const engagementTimelineView = new LearnerEngagementTimelineView({
        model: timelineModel,
      });
      const engagementTableView = new LearnerEngagementTableView({
        model: timelineModel,
      });
      let chartView = engagementTimelineView;
      let tableView = engagementTableView;
      if (!timelineModel.hasData()) {
        // instead of showing the timeline directly, show a loading view
        chartView = new LoadingView({
          model: timelineModel,
          template: _.template(chartLoadingTemplate),
          successView: engagementTimelineView,
        });
        tableView = new LoadingView({
          model: timelineModel,
          template: _.template(tableLoadingTemplate),
          successView: engagementTableView,
        });
      }

      this.showChildView('names', new LearnerNameView({
        model: learnerModel,
        trackingModel: this.options.trackingModel,
      }));

      this.showChildView('enrollment', new LearnerSummaryFieldView({
        model: learnerModel,
        modelAttribute: 'enrollment_mode',
        fieldDisplayName: gettext('Enrollment'),
      }));

      this.showChildView('cohort', new LearnerSummaryFieldView({
        model: learnerModel,
        modelAttribute: 'cohort',
        fieldDisplayName: gettext('Cohort'),
      }));
      this.showChildView('accessed', new LearnerSummaryFieldView({
        model: timelineModel,
        modelAttribute: 'days',
        fieldDisplayName: gettext('Last Accessed'),
        valueFormatter(days) {
          // Translators: 'n/a' means 'not available'
          return days.length ? Utils.formatDate(_(days).last().date) : gettext('n/a');
        },
      }));
      this.showChildView('engagementTimeline', chartView);
      this.showChildView('engagementTable', tableView);
    },

    showLearnerUnavailable(options) {
      this.showUnavailable('learnerSummary', options);
    },

    showTimelineUnavailable(options) {
      this.showUnavailable('engagementTimeline', options);
    },

    showUnavailable(region, options) {
      const tableSection = document.getElementById('table-section');
      this.showChildView(region, new AlertView({
        alertType: 'info',
        title: options.title,
        body: options.description,
      }));
      this.getRegion('engagementTable').empty();
      tableSection.parentElement.removeChild(tableSection);
    },

    serverErrorToAppError(status, unavailableError) {
      if (status === 404) {
        return [unavailableError.errorType, {
          title: unavailableError.title,
          description: gettext('Check back daily for up-to-date data.'),
        }];
      }
      return ListUtils.EventTransformers.serverErrorToAppError(status);
    },

    timelineServerErrorToAppError(status) {
      return this.serverErrorToAppError(status, {
        errorType: 'engagementTimelineUnavailable',
        title: gettext('No course activity data is available for this learner.'),
      });
    },

    learnerServerErrorToAppError(status) {
      return this.serverErrorToAppError(status, {
        errorType: 'learnerUnavailable',
        title: gettext('No learner data is available.'),
      });
    },

  });
});
