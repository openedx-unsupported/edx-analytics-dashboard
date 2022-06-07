define(
  ['moment', 'nvd3', 'underscore', 'views/stacked-trends-view', 'utils/utils'],
  (moment, nvd3, _, StackedTrendsView, Utils) => {
    'use strict';

    const StackedTimelineView = StackedTrendsView.extend({

      formatXTick(d) {
        return Utils.formatTime(d);
      },

      parseXData(d) {
        const self = this;
        return d[self.options.x.key];
      },

    });

    return StackedTimelineView;
  },
);
