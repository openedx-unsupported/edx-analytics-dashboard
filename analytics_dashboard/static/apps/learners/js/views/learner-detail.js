define([
    'learners/js/utils',
    'learners/js/views/engagement-timeline',
    'learners/js/views/loading-view',
    'marionette',
    'text!learners/templates/chart-loading.underscore',
    'text!learners/templates/learner-detail.underscore',
    'underscore'
], function (
    LearnerUtils,
    LearnerEngagementTimelineView,
    LoadingView,
    Marionette,
    chartLoadingTemplate,
    learnerDetailTemplate,
    _
) {
    'use strict';

    var LearnerDetailView = Marionette.LayoutView.extend({
        className: 'learner-detail-container',
        template: _.template(learnerDetailTemplate),
        regions: {
            engagementTimeline: '.learner-engagement-timeline-container'
        },
        initialize: function (options) {
            Marionette.LayoutView.prototype.initialize.call(this, options);
            this.options = options || {};

            LearnerUtils.mapEvents(this.options.engagementTimelineModel, {
                serverError: LearnerUtils.EventTransformers.serverErrorToAppError,
                networkError: LearnerUtils.EventTransformers.networkErrorToAppError,
                sync: LearnerUtils.EventTransformers.syncToClearError
            }, this);
        },
        onAppError: function () {
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
        }
    });

    return LearnerDetailView;
});
