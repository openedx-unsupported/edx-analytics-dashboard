define(['moment', 'nvd3', 'underscore', 'views/stacked-trends-view', 'utils/utils'],
    function (moment, nvd3, _, StackedTrendsView, Utils) {
        'use strict';

        var StackedTimelineView = StackedTrendsView.extend({

            formatXTick: function (d) {
                return Utils.formatTime(d);
            },

            parseXData: function (d) {
                var self = this;
                return d[self.options.x.key];
            }

        });

        return StackedTimelineView;
    }
);
