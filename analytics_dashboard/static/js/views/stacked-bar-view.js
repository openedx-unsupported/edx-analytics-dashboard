define(['nvd3', 'underscore', 'views/discrete-bar-view'],
    function (nvd3, _, DiscreteBarView) {
        'use strict';

        var StackedBarView = DiscreteBarView.extend({

            defaults: _.extend({}, DiscreteBarView.prototype.defaults, {
                    barSelector: '.nv-bar'
                }
            ),

            getChart: function () {
                return nvd3.models.multiBarChart();
            },

            initChart: function (chart) {
                var self = this;
                DiscreteBarView.prototype.initChart.call(self, chart);

                chart.stacked(true)
                    .showControls(false)
                    .showLegend(false);

                chart.tooltipContent(function(key, x, y, e) {
                    var tips = [];
                    _(self.options.trends).each(function(trend) {
                        var trendY = self.getYAxisFormat()(e.point[trend.key]);
                        tips.push(self.buildTrendTip(trend, x, trendY, e));
                    });

                    return self.hoverTooltipTemplate({
                        xValue: self.buildTipHeading(e.point),
                        tips: tips
                    });
                });
            }

        });

        return StackedBarView;
    });
