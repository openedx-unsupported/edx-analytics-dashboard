define([
    'marionette',
    'text!learners/templates/engagement-timeline.underscore',
    'views/trends-view',
    'underscore'
], function (Marionette, engagementTimelineTemplate, TrendsView, _) {
    'use strict';

    var LearnerEngagementTimelineView = Marionette.LayoutView.extend({
        template: _.template(engagementTimelineTemplate),
        regions: {
            main: '.learner-engagement-timeline.analytics-chart'
        },
        onAttach: function () {
            // Normally we'd declare this logic in the
            // `Marionette.View.onBeforeView` method, but the TrendsView
            // requires that the chart's container element is in the DOM.
            new TrendsView({
                showLegend: true,
                el: this.regions.main,
                model: this.model,
                modelAttribute: 'days',
                isDataAvailable: function () {
                    return this.model.get('days').length > 0;
                },
                trends: [{
                    key: 'discussion_contributions',
                    title: gettext('Discussion Contributions'),
                    type: 'number'
                }, {
                    key: 'problems_completed',
                    title: gettext('Problems Completed'),
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
        }
    });

    return LearnerEngagementTimelineView;
});
