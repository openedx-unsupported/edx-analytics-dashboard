define([
    'learners/js/utils',
    'learners/js/views/engagement-timeline',
    'marionette',
    'text!learners/templates/learner-detail.underscore',
    'underscore'
], function (
    LearnerUtils,
    LearnerEngagementTimelineView,
    Marionette,
    learnerDetailTemplate,
    _
) {
    'use strict';

    var LearnerDetailView = Marionette.LayoutView.extend({
        className: 'learner-detail-container',
        template: _.template(learnerDetailTemplate),
        regions: {
            engagementTimeline: '.learner-engagement-timeline-container.analytics-chart-container'
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
        onBeforeShow: function () {
            this.showChildView('engagementTimeline', new LearnerEngagementTimelineView({
                model: this.options.engagementTimelineModel
            }));
        }
    });

    return LearnerDetailView;
});
