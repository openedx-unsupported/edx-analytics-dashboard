define(function (require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        LearnerEngagementTimelineView = require('learners/detail/views/engagement-timeline'),
        LearnerUtils = require('learners/common/utils'),
        LoadingView = require('learners/common/views/loading-view'),
        chartLoadingTemplate = require('text!learners/detail/templates/chart-loading.underscore'),
        learnerDetailTemplate = require('text!learners/detail/templates/learner-detail.underscore'),

        LearnerDetailView;

    LearnerDetailView = Marionette.LayoutView.extend({
        className: 'learner-detail-container',

        template: _.template(learnerDetailTemplate),

        regions: {
            engagementTimeline: '.learner-engagement-timeline-container'
        },

        initialize: function (options) {
            Marionette.LayoutView.prototype.initialize.call(this, options);
            this.options = options || {};
            LearnerUtils.mapEvents(this.options.engagementTimelineModel, {
                serverError: this.serverErrorToAppError,
                networkError: LearnerUtils.EventTransformers.networkErrorToAppError,
                sync: LearnerUtils.EventTransformers.syncToClearError
            }, this);
        },

        onAppWarning: function () {
            this.removeRegion('engagementTimeline');
        },

        onBeforeShow: function () {
            var timelineModel = this.options.engagementTimelineModel,
                timelineView = new LearnerEngagementTimelineView({
                    model: timelineModel
                }),
                mainView = timelineView;

            if (!timelineModel.hasData()) {
                // instead of showing the timeline direction, show a loading view
                mainView = new LoadingView({
                    model: timelineModel,
                    template: _.template(chartLoadingTemplate),
                    successView: timelineView
                });
            }

            this.showChildView('engagementTimeline', mainView);
        },

        serverErrorToAppError: function (status) {
            if (status === 404) {
                return ['appWarning', {
                    title: gettext('No course activity data is available for this learner.'),
                    description: gettext('Check back daily for up-to-date data.')
                }];
            } else {
                return LearnerUtils.EventTransformers.serverErrorToAppError(status);
            }
        }
    });

    return LearnerDetailView;
});
