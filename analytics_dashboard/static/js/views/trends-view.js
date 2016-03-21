define(['moment', 'nvd3', 'underscore', 'views/chart-view'],
    function (moment, nvd3, _, ChartView) {
        'use strict';

        /**
         * TrendsView renders several threads of timeline data over a period of
         * time on the x axis.
         */
        var TrendsView = ChartView.extend({

            /**
             * Initializes a TrendsView.
             *
             * @param options (Object) an object specifying view parameters.
             * In addition to parameters passed to 'ChartView', this options
             * hash must include:
             *  - trends (Array of Objects) defines timeline trends:
             *      [{
             *          key: str,   // key for data lookup
             *          title: str, // display name (should be translated)
             *          type: str   // data type
             *      }, ...]
             *  - x (Object) defines how to find x axis data:
             *      {
             *          title: str, // display name (translated) for the X axis
             *          key: str    // key for the data lookup
             *      }
             *  - y (Object) defines how to find y axis data:
             *      {
             *          title: str // display name (translated) for the X axis
             *          key: str   // key for the data lookup
             *      }
             */
            initialize: function (options) {
                ChartView.prototype.initialize.call(this, options);
            },

            defaults: _.extend({}, ChartView.prototype.defaults, {
                showLegend: false
            }),

            getChart: function () {
                return nvd3.models.lineChart();
            },

            initChart: function (chart) {
                ChartView.prototype.initChart.call(this, chart);
                var self = this;

                chart.showLegend(this.options.showLegend)
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
