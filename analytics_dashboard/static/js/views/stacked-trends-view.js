define(
  ['underscore', 'nvd3', 'views/trends-view'],
  (_, nvd3, TrendsView) => {
    'use strict';

    const StackedTrendsView = TrendsView.extend({
      defaults: _.extend({}, TrendsView.prototype.defaults, {
        graphShiftSelector: '.nv-stackedarea',
      }),

      getChart() {
        return nvd3.models.stackedAreaChart().showControls(false);
      },

      render() {
        const self = this;
        TrendsView.prototype.render.call(self);

        // Disable expansion of stacked chart datasets
        self.chart.stacked.dispatch.on('areaClick', null);
        self.chart.stacked.dispatch.on('areaClick.toggle', null);

        return self;
      },
    });

    return StackedTrendsView;
  },
);
