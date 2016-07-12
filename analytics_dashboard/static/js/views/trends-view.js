define(['moment', 'nvd3', 'underscore', 'views/chart-view'],
    function(moment, nvd3, _, ChartView) {
        'use strict';

        /**
         * TrendsView renders several threads of timeline data over a period of
         * time on the x axis.
         */
        var TrendsView = ChartView.extend({

            defaults: _.extend({}, ChartView.prototype.defaults, {
                showLegend: false
            }),

            getChart: function() {
                return nvd3.models.lineChart();
            },

            initChart: function(chart) {
                ChartView.prototype.initChart.call(this, chart);
                var self = this;

                chart.showLegend(this.options.showLegend)
                    .useInteractiveGuideline(true);

                if (_(self.options).has('interactiveTooltipHeaderTemplate')) {
                    self.chart.interactiveLayer.tooltip.headerFormatter(function(d) {
                        return self.options.interactiveTooltipHeaderTemplate({value: d});
                    });
                }
            },

            formatXTick: function(d) {
                // overriding default to display a formatted date
                return moment(d).format('M/D');
            },

            parseXData: function(d) {
                var self = this;
                return Date.parse(d[self.options.x.key]);
            }

        });

        return TrendsView;
    }
);
