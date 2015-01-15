/**
 * Abstract class for NVD3 bar charts (includes discrete bar and histogram).
 */
define(['nvd3', 'underscore', 'utils/utils', 'views/chart-view'],
    function (nvd3, _, Utils, ChartView) {
        'use strict';

        var BarView = ChartView.extend({

            defaults: _.extend({}, ChartView.prototype.defaults, {
                    graphShiftSelector: '.nv-barsWrap',
                    tipCharLimit: 250  // clip and add ellipses to long tooltips
                }
            ),

            /**
             * Returns the x-value/label displayed on the chart.  Further formatting (e.g. adding ellipse)
             * should be done in formatXTick (see DiscreteBarView) for labels beneath the bars.
             *
             * This is called for both display labels beneath the bars and in tooltips.
             */
            formatXValue: function(xValue) {
                var self = this,
                    trend = self.options.trends[0],
                    maxNumber = trend.maxNumber;

                if (!_(maxNumber).isUndefined()) {
                    // e.g. 100+
                    xValue = xValue >= maxNumber ? maxNumber + '+' : xValue;
                }

                return xValue;
            },

            initChart: function(chart) {
                var self = this;
                ChartView.prototype.initChart.call(self, chart);

                // NVD3's bar views display tooltips differently than for graphs
                chart.tooltipContent(function(key, x, y, e) {
                    var trend = self.options.trends[0],
                        // 'e' contains the raw x-value and 'x' could be formatted (e.g. truncated, ellipse, etc.)
                        xValue = self.formatXValue(e.point[self.options.x.key]),
                        swatchColor = trend.color,  // e.g #ff9988 or a function
                        label = trend.title,  // e.g. 'my title' or a function
                        tipText = xValue;

                    // bar colors can be dynamically assigned based on value
                    if (_(swatchColor).isFunction()) {
                        swatchColor = trend.color(x, e.pointIndex);
                    }

                    // bar label can be dynamically assigned based on value
                    if (_(label).isFunction()) {
                        label = trend.title(e.pointIndex);
                    }

                    // create the tooltip when hovering over a bar
                    if (_(self.options).has('interactiveTooltipHeaderTemplate')) {
                        if (_(self.options).has('tipCharLimit')) {
                            // truncate long labels in the tooltips
                            if (_(xValue).size() > self.options.tipCharLimit) {
                                tipText = Utils.truncateText(xValue, self.options.tipCharLimit);

                            }
                        }
                        tipText = self.options.interactiveTooltipHeaderTemplate({value: tipText});
                    }

                    return self.hoverTooltipTemplate({
                        xValue: tipText,
                        label: label,
                        yValue: y,
                        swatchColor: swatchColor
                    });
                });
            }

        });

        return BarView;
    }
);
