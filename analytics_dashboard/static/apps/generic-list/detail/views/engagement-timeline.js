define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        TrendsView = require('views/trends-view'),
        engagementTimelineTemplate = require('text!learners/detail/templates/engagement-timeline.underscore'),

        LearnerEngagementTimelineView;

    LearnerEngagementTimelineView = Marionette.LayoutView.extend({
        template: _.template(engagementTimelineTemplate),
        regions: {
            main: '.learner-engagement-timeline.analytics-chart'
        },
        onAttach: function() {
            // Normally we'd declare this logic in the
            // `Marionette.View.onBeforeView` method, but the TrendsView
            // requires that the chart's container element is in the DOM.
            var learnerEngagementChart = new TrendsView({
                showLegend: true,
                el: this.regions.main,
                model: this.model,
                modelAttribute: 'days',
                isDataAvailable: function() {
                    return this.model.hasData();
                },
                trends: [{
                    key: 'discussion_contributions',
                    title: gettext('Discussion Contributions'),
                    type: 'number'
                }, {
                    key: 'problems_completed',
                    title: gettext('Problems Correct'),
                    type: 'number'
                }, {
                    key: 'videos_viewed',
                    title: gettext('Videos Viewed'),
                    type: 'number'
                }],
                x: {
                    title: gettext('Date'),
                    key: 'date'
                },
                y: {
                    title: gettext('Value'), // TODO: doc review of y-axis display name
                    key: 'value'
                }
            });
            learnerEngagementChart.renderIfDataAvailable();
        }
    });

    return LearnerEngagementTimelineView;
});
