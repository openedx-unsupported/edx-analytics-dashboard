define(['moment', 'nvd3', 'underscore', 'views/chart-view'],
    function (moment, nvd3, _, ChartView) {
        'use strict';

        var TrendsView = ChartView.extend({

            getChart: function () {
                return nvd3.models.lineChart();
            },

            initChart: function (chart) {
                ChartView.prototype.initChart.call(this, chart);
                chart.showLegend(false)
                    .useInteractiveGuideline(true);
            },

            formatXTick: function (d) {
                // overriding default to display a formatted date
                return moment(d).zone('+0000').format('M/D');
            },

            parseXData: function (d) {
                var self = this;
                return Date.parse(d[self.options.x.key]);
            }

        });

        return TrendsView;
    }
);
