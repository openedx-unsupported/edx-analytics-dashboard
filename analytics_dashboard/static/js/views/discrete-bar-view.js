define(
  ['d3', 'nvd3', 'underscore', 'utils/utils', 'views/bar-view'],
  (d3, nvd3, _, Utils, BarView) => {
    'use strict';

    const DiscreteBarView = BarView.extend({

      defaults: _.extend({}, BarView.prototype.defaults, {
        // unsetting because this view will always display all x-ticks
        displayExplicitTicksThreshold: undefined,
        barSelector: '.discreteBar',
      }),

      /**
             * Returns the original bar label or "(empty)" if no label provided.
             */
      formatXValue(xValue) {
        const self = this;
        const formattedXValue = BarView.prototype.formatXValue.call(self, xValue);
        // Translators: (empty) is displayed as a label in a chart and indicates that no label was provided.
        return _(formattedXValue).isNull() ? gettext('(empty)') : formattedXValue;
      },

      getChart() {
        return nvd3.models.discreteBarChart();
      },

      initChart(chart) {
        const self = this;
        BarView.prototype.initChart.call(self, chart);

        if (_(self.options.trends[0]).has('color')) {
          if (_(self.options.trends[0].color).isFunction()) {
            chart.color(self.options.trends[0].color);
          } else {
            chart.color([self.options.trends[0].color]);
          }
        }
      },

    });

    return DiscreteBarView;
  },
);
