define(['d3', 'nvd3', 'underscore', 'utils/utils', 'views/bar-view'],
    function (d3, nvd3, _, Utils, BarView) {
        'use strict';

        var DiscreteBarView = BarView.extend({

            defaults: _.extend({}, BarView.prototype.defaults, {
                    // unsetting because this view will always display all x-ticks
                    displayExplicitTicksThreshold: undefined
                }
            ),

            ///**
            // * Add ellipses for long labels shown beneath the bar.
            // */
            //formatXTick: function (d) {
            //    var barWidth = d3.select('.discreteBar').attr('width'),
            //        // this is a rough estimate of how wide a character is
            //        chartWidth = 5,
            //        characterLimit = Math.floor(barWidth / chartWidth),
            //        formattedLabel = d;
            //
            //    if (_(formattedLabel).size() > characterLimit) {
            //        formattedLabel = Utils.truncateText(d, characterLimit);
            //    }
            //
            //    return formattedLabel;
            //},

            /**
             * Returns the original bar label or "(empty)" if no label provided.
             */
            formatXValue: function (xValue) {
                var self = this;
                xValue = BarView.prototype.formatXValue.call(self, xValue);
                // Translators: (empty) is displayed as a label in a chart and indicates that no label was provided.
                return _(xValue).isNull() ? gettext('(empty)') : xValue;
            },

            parseXData: function (d) {
                var self = this,
                    value = BarView.prototype.parseXData.call(self, d);
                return self.formatXValue(value);
            },

            getChart: function () {
                return nvd3.models.discreteBarChart();
            },

            initChart: function (chart) {
                var self = this;
                BarView.prototype.initChart.call(self, chart);

                if (_(self.options.trends[0]).has('color')) {
                    if (_(self.options.trends[0].color).isFunction()) {
                        chart.color(self.options.trends[0].color);
                    } else {
                        chart.color([self.options.trends[0].color]);
                    }
                }
            }

        });

        return DiscreteBarView;
    }
);
