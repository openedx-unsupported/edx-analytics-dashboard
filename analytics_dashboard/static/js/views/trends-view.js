define(
  ['moment', 'nvd3', 'underscore', 'views/chart-view'],
  (moment, nvd3, _, ChartView) => {
    'use strict';

    /**
         * TrendsView renders several threads of timeline data over a period of
         * time on the x axis.
         */
    const TrendsView = ChartView.extend({

      defaults: _.extend({}, ChartView.prototype.defaults, {
        showLegend: false,
      }),

      getChart() {
        return nvd3.models.lineChart();
      },

      initChart(chart) {
        const self = this;
        ChartView.prototype.initChart.call(this, chart);

        chart.showLegend(this.options.showLegend)
          .useInteractiveGuideline(true);

        if (_(self.options).has('interactiveTooltipHeaderTemplate')) {
          self.chart.interactiveLayer.tooltip.headerFormatter(
            (d) => self.options.interactiveTooltipHeaderTemplate({ value: self.formatXTick(d) }),
          );
        }
      },

      formatXTick(d) {
        // overriding default to display a formatted date
        return moment.utc(d).format('D MMM YYYY');
      },

      parseXData(d) {
        const self = this;
        return Date.parse(d[self.options.x.key]);
      },

    });

    return TrendsView;
  },
);
