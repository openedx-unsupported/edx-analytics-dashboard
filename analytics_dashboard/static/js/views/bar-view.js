/**
 * Abstract class for NVD3 bar charts (includes discrete bar and histogram).
 */
define(['nvd3', 'underscore', 'views/chart-view'],
    function (nvd3, _, ChartView) {
        'use strict';

        var BarView = ChartView.extend({

            defaults: _.extend({}, ChartView.prototype.defaults, {
                    graphShiftSelector: '.nv-barsWrap'
                }
            ),

            initChart: function(chart) {
                var self = this;
                ChartView.prototype.initChart.call(self, chart);

                // NVD3's bar views display tooltips differently than for graphs
                chart.tooltipContent(function(key, x, y) {
                    var maxNumber = self.options.trends[0].maxNumber,
                        xValue = x;

                    if (!_(maxNumber).isUndefined) {
                        // e.g. 100+
                        xValue = x >= maxNumber ? maxNumber + '+' : x;
                    }

                    if (_(self.options).has('interactiveTooltipHeaderTemplate')) {
                        xValue = self.options.interactiveTooltipHeaderTemplate({value: xValue});
                    }

                    return self.hoverTooltipTemplate({
                        xValue: xValue,
                        label: key,
                        yValue: y,
                        swatchColor: self.options.trends[0].color
                    });
                });
            }

        });

        return BarView;
    }
);
