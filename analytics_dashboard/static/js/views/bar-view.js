/**
 * Abstract class for NVD3 bar charts (includes discrete bar and histogram).
 */
define(['d3', 'nvd3', 'underscore', 'utils/utils', 'views/chart-view'],
    function (d3, nvd3, _, Utils, ChartView) {
        'use strict';

        var BarView = ChartView.extend({

            defaults: _.extend({}, ChartView.prototype.defaults, {
                    graphShiftSelector: '.nv-barsWrap',
                    tipCharLimit: 250,  // clip and add ellipses to long tooltips
                    barSelector: '.nv-bar'
                }
            ),

            /**
             * Returns the x-value/label displayed on the chart.  Further formatting (e.g. adding ellipse)
             * should be done in formatXTick (see DiscreteBarView) for labels beneath the bars.
             *
             * This is called for both display labels beneath the bars and in tooltips.
             */
            formatXValue: function (xValue) {
                var self = this,
                    trend = self.options.trends[0],
                    maxNumber = trend.maxNumber;

                xValue = ChartView.prototype.formatXTick.call(self, xValue);

                if (!_(maxNumber).isUndefined()) {
                    // e.g. 100+
                    xValue = xValue >= maxNumber ? maxNumber + '+' : xValue;
                }

                return xValue;
            },

            /**
             * Returns function for displaying a truncated label.
             */
            truncateXTick: function (d) {
                var self = this;
                d = self.formatXValue(d);

                var barWidth = d3.select(self.options.barSelector).attr('width'),  // jshint ignore:line
                // this is a rough estimate of how wide a character is
                    charWidth = 6,
                    characterLimit = Math.floor(barWidth / charWidth),
                    formattedLabel = d;

                if (characterLimit < 3) {
                    // no labels will be displayed if label space is limited
                    formattedLabel = '';
                } else if (_(formattedLabel).size() > characterLimit) {
                    formattedLabel = Utils.truncateText(d, characterLimit);
                }

                return formattedLabel;
            },

            addChartClick: function () {
                var self = this;
                d3.selectAll('rect.nv-bar')
                    .style('cursor', 'pointer')
                    .on('click', function (d) {
                        self.options.click(d);
                    });
            },

            buildTrendTip: function (trend, x, y, e) {
                var self = this,
                    swatchColor = trend.color,  // e.g #ff9988 or a function
                    label = trend.title;  // e.g. 'my title' or a function

                // bar colors can be dynamically assigned based on value
                if (_(swatchColor).isFunction()) {
                    swatchColor = trend.color(x, e.pointIndex);
                } else {
                    swatchColor = trend.color;
                }

                // bar label can be dynamically assigned based on value
                if (_(label).isFunction()) {
                    label = trend.title(e.pointIndex);
                } else {
                    label = trend.title;
                }

                if (_(self.options).has('interactiveTooltipValueTemplate')) {
                    y = self.options.interactiveTooltipValueTemplate({value: y, point: e.point, options: trend});
                }

                return {
                    label: label,
                    color: swatchColor,
                    value: y
                };
            },

            /**
             * Builds the header for the interactive tooltip.
             */
            buildTipHeading: function (point) {
                var self = this,
                    heading = self.formatXValue(point[self.options.x.key]),
                    charLimit = self.options.tipCharLimit;

                // create the tooltip when hovering over a bar
                if (_(self.options).has('interactiveTooltipHeaderTemplate')) {
                    if (_(self.options).has('tipCharLimit')) {
                        // truncate long labels in the tooltips
                        if (_(heading).size() > charLimit) {
                            heading = Utils.truncateText(heading, charLimit);
                        }
                    }
                    heading = self.options.interactiveTooltipHeaderTemplate({value: heading});
                }

                return heading;
            },

            initChart: function (chart) {
                var self = this;
                ChartView.prototype.initChart.call(self, chart);

                // NVD3's bar views display tooltips differently than for graphs
                chart.tooltipContent(function (key, x, y, e) {
                    var trend = self.options.trends[e.seriesIndex],
                    // 'e' contains the raw x-value and 'x' could be formatted (e.g. truncated, ellipse, etc.)
                        tips = [self.buildTrendTip(trend, x, y, e)];

                    return self.hoverTooltipTemplate({
                        xValue: self.buildTipHeading(e.point),
                        tips: tips
                    });
                });
            }
        });

        return BarView;
    }
);
