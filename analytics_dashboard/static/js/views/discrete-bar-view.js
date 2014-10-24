define(['nvd3', 'underscore', 'views/chart-view'],
    function (nvd3, _, ChartView) {
        'use strict';

        var DiscreteBarView = ChartView.extend({

            defaults: _.extend({}, ChartView.prototype.defaults, {
                    // unsetting because this view will always display all x-ticks
                    displayExplicitTicksThreshold: undefined,
                    graphShiftSelector: '.nv-barsWrap'
                }
            ),

            getChart: function() {
                return nvd3.models.discreteBarChart();
            },

            initChart: function(chart) {
                var self = this;
                ChartView.prototype.initChart.call(self, chart);

                if (_(self.options.trends[0]).has('color')) {
                    chart.color([self.options.trends[0].color]);
                }

                chart.tooltipContent(function(key, x, y) {
                    var maxNumber = self.options.trends[0].maxNumber,
                        xValue = x;

                    if (!_(maxNumber).isUndefined) {
                        // e.g. 100+
                        xValue = x >= maxNumber ? maxNumber + '+' : x;
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

        return DiscreteBarView;
    }
);
