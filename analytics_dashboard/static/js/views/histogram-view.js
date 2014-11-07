define(['nvd3', 'underscore', 'views/bar-view'],
    function (nvd3, _, BarView) {
        'use strict';

        var HistogramView = BarView.extend({

            getChart: function() {
                return nvd3.models.multiBarChart();
            },

            initChart: function(chart) {
                BarView.prototype.initChart.call(this, chart);

                chart.showLegend(false);
                chart.multibar.stacked(true);
                chart.showControls(false);
            }

        });

        return HistogramView;
    }
);
