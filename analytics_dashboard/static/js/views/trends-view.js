define(['moment', 'nvd3', 'underscore', 'views/chart-view'],
    function (moment, nvd3, _, ChartView) {
        'use strict';

        var TrendsView = ChartView.extend({

            getChart: function () {
                return nvd3.models.lineChart();
            },

            initChart: function (chart) {
                ChartView.prototype.initChart.call(this, chart);
                var self = this;

                chart.showLegend(false)
                    .useInteractiveGuideline(true);

                if (_(self.options).has('interactiveTooltipHeaderTemplate')) {
                    self.chart.interactiveLayer.tooltip.headerFormatter(function (d) {
                        return self.options.interactiveTooltipHeaderTemplate({value: d});
                    });
                }
            },

            formatXTick: function (d) {
                // overriding default to display a formatted date
                return moment(d).format('M/D');
            },

            parseXData: function (d) {
                var self = this;
                return Date.parse(d[self.options.x.key]);
            }

        });

        return TrendsView;
    }
);
