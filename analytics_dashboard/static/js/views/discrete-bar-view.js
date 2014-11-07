define(['nvd3', 'underscore', 'views/bar-view'],
    function (nvd3, _, BarView) {
        'use strict';

        var DiscreteBarView = BarView.extend({

            defaults: _.extend({}, BarView.prototype.defaults, {
                    // unsetting because this view will always display all x-ticks
                    displayExplicitTicksThreshold: undefined
                }
            ),

            getChart: function() {
                return nvd3.models.discreteBarChart();
            },

            initChart: function(chart) {
                var self = this;
                BarView.prototype.initChart.call(self, chart);

                if (_(self.options.trends[0]).has('color')) {
                    chart.color([self.options.trends[0].color]);
                }
            }

        });

        return DiscreteBarView;
    }
);
