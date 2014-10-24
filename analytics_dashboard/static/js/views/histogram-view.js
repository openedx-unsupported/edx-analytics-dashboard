define(['nvd3', 'underscore', 'views/chart-view'],
    function (nvd3, _, ChartView) {
        'use strict';

        var HistogramView = ChartView.extend({
            defaults: _.extend({}, ChartView.prototype.defaults, {
                    graphShiftSelector: '.nv-barsWrap'
                }
            ),

            getChart: function() {
                return nvd3.models.multiBarChart();
            },

            initChart: function(chart) {
                ChartView.prototype.initChart.call(this, chart);
                var self = this;

                chart.showLegend(false);
                chart.multibar.stacked(true);
                chart.showControls(false);

                chart.tooltip(function(key, x, y) {
                    var maxNumber = self.options.trends[0].maxNumber;
                    return self.hoverTooltipTemplate({
                        xValue: x >= maxNumber ? maxNumber + '+' : x,  // e.g. 100+
                        label: key,
                        yValue: y,
                        swatchColor: self.options.trends[0].color
                    });
                });

            }

        });

        return HistogramView;
    }
);
