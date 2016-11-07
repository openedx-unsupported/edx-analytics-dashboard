define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        LearnerUtils = require('learners/common/utils'),
        Utils = require('utils/utils'),

        AlertView = require('learners/common/views/alert-view'),
        LearnerEngagementTableView = require('learners/detail/views/engagement-table'),
        LearnerEngagementTimelineView = require('learners/detail/views/engagement-timeline'),
        LearnerNameView = require('learners/detail/views/learner-names'),
        LearnerSummaryFieldView = require('learners/detail/views/learner-summary-field'),
        LoadingView = require('learners/common/views/loading-view'),
        chartLoadingTemplate = require('text!learners/detail/templates/chart-loading.underscore'),
        tableLoadingTemplate = require('text!learners/detail/templates/table-loading.underscore'),
        learnerDetailTemplate = require('text!learners/detail/templates/learner-detail.underscore');

    return Marionette.LayoutView.extend({
        className: 'learner-detail-container',

        template: _.template(learnerDetailTemplate),

        templateHelpers: function() {
            return {
                // Translators: e.g. Learner engagement activity
                engagement: gettext('Engagement Activity'),
                activity: gettext('Daily Activity'),
                table: gettext('Activity Over Time')
            };
        },

        regions: {
            learnerSummary: '.learner-summary-container',
            names: '.learner-names',
            enrollment: '.learner-enrollment',
            cohort: '.learner-cohort',
            accessed: '.learner-accessed',
            engagementTimeline: '.learner-engagement-timeline-container',
            engagementTable: '.learner-engagement-table-container'
        },

        initialize: function(options) {
            Marionette.LayoutView.prototype.initialize.call(this, options);
            this.options = options || {};
            LearnerUtils.mapEvents(this.options.engagementTimelineModel, {
                serverError: this.timelineServerErrorToAppError,
                networkError: LearnerUtils.EventTransformers.networkErrorToAppError,
                sync: LearnerUtils.EventTransformers.syncToClearError
            }, this);
            this.listenTo(this, 'engagementTimelineUnavailable', this.showTimelineUnavailable);

            LearnerUtils.mapEvents(this.options.learnerModel, {
                serverError: this.learnerServerErrorToAppError,
                networkError: LearnerUtils.EventTransformers.networkErrorToAppError,
                sync: LearnerUtils.EventTransformers.syncToClearError
            }, this);
            this.listenTo(this, 'learnerUnavailable', this.showLearnerUnavailable);
        },

        onBeforeShow: function() {
            var learnerModel = this.options.learnerModel,
                timelineModel = this.options.engagementTimelineModel,
                engagementTimelineView = new LearnerEngagementTimelineView({
                    model: timelineModel
                }),
                engagementTableView = new LearnerEngagementTableView({
                    model: timelineModel
                }),
                chartView = engagementTimelineView,
                tableView = engagementTableView;
            if (!timelineModel.hasData()) {
                // instead of showing the timeline directly, show a loading view
                chartView = new LoadingView({
                    model: timelineModel,
                    template: _.template(chartLoadingTemplate),
                    successView: engagementTimelineView
                });
                tableView = new LoadingView({
                    model: timelineModel,
                    template: _.template(tableLoadingTemplate),
                    successView: engagementTableView
                });
            }

            this.showChildView('names', new LearnerNameView({
                model: learnerModel,
                trackingModel: this.options.trackingModel
            }));

            this.showChildView('enrollment', new LearnerSummaryFieldView({
                model: learnerModel,
                modelAttribute: 'enrollment_mode',
                fieldDisplayName: 'Enrollment'
            }));

            this.showChildView('cohort', new LearnerSummaryFieldView({
                model: learnerModel,
                modelAttribute: 'cohort',
                fieldDisplayName: 'Cohort'
            }));
            this.showChildView('accessed', new LearnerSummaryFieldView({
                model: timelineModel,
                modelAttribute: 'days',
                fieldDisplayName: 'Last Accessed',
                valueFormatter: function(days) {
                    // Translators: 'n/a' means 'not available'
                    return days.length ? Utils.formatDate(_(days).last().date) : gettext('n/a');
                }
            }));
            this.showChildView('engagementTimeline', chartView);
            this.showChildView('engagementTable', tableView);
        },

        showLearnerUnavailable: function(options) {
            this.showUnavailable('learnerSummary', options);
        },

        showTimelineUnavailable: function(options) {
            this.showUnavailable('engagementTimeline', options);
        },

        showUnavailable: function(region, options) {
            var tableSection = document.getElementById('table-section');
            this.showChildView(region, new AlertView({
                alertType: 'info',
                title: options.title,
                body: options.description
            }));
            this.getRegion('engagementTable').empty();
            tableSection.parentElement.removeChild(tableSection);
        },

        serverErrorToAppError: function(status, unavailableError) {
            if (status === 404) {
                return [unavailableError.errorType, {
                    title: unavailableError.title,
                    description: gettext('Check back daily for up-to-date data.')
                }];
            } else {
                return LearnerUtils.EventTransformers.serverErrorToAppError(status);
            }
        },

        timelineServerErrorToAppError: function(status) {
            return this.serverErrorToAppError(status, {
                errorType: 'engagementTimelineUnavailable',
                title: gettext('No course activity data is available for this learner.')
            });
        },

        learnerServerErrorToAppError: function(status) {
            return this.serverErrorToAppError(status, {
                errorType: 'learnerUnavailable',
                title: gettext('No learner data is available.')
            });
        }

    });
});
