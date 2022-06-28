define(
  ['nvd3', 'underscore', 'views/bar-view'],
  (nvd3, _, BarView) => {
    'use strict';

    const HistogramView = BarView.extend({

      getChart() {
        return nvd3.models.multiBarChart();
      },

      initChart(chart) {
        BarView.prototype.initChart.call(this, chart);

        chart.showLegend(false);
        chart.multibar.stacked(true);
        chart.showControls(false);
      },

    });

    return HistogramView;
  },
);
