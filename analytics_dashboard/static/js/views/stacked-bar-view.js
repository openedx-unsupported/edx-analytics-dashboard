define(['nvd3', 'underscore', 'views/discrete-bar-view'],
    function (nvd3, _, DiscreteBarView) {
        'use strict';

        var StackedBarView = DiscreteBarView.extend({

            defaults: _.extend({}, DiscreteBarView.prototype.defaults, {
                    // unsetting because this view will always display all x-ticks
                    displayExplicitTicksThreshold: undefined
                }
            ),

            getChart: function () {
                return nvd3.models.multiBarChart();
            },

            initChart: function (chart) {
                var self = this;
                DiscreteBarView.prototype.initChart.call(self, chart);

                chart
                    .color(null)
                    // TODO Create a stacked chart that subtracts specific values from the total.
                    //.stacked(true)
                    .showControls(false)
                    .showLegend(true);
            },

            render: function () {
                var self = this;
                DiscreteBarView.prototype.render.call(this);

                // Disable clicking on the legend since we don't properly restyle the chart after data changes.
                var emptyEventHandler = function () {
                };

                for (var property in self.chart.legend.dispatch) {
                    self.chart.legend.dispatch[property] = emptyEventHandler;
                }
            }

        });

        return StackedBarView;
    });
