define(['nvd3', 'views/trends-view'],
    function (nvd3, TrendsView) {
        'use strict';

        var StackedTrendsView = TrendsView.extend({
            defaults: _.extend({}, TrendsView.prototype.defaults, {
                    graphShiftSelector: '.nv-stackedarea'
                }
            ),

            getChart: function () {
                return nvd3.models.stackedAreaChart().showControls(false);
            },

            render: function () {
                var self = this;
                TrendsView.prototype.render.call(self);

                // Disable expansion of stacked chart datasets
                self.chart.stacked.dispatch.on('areaClick', null);
                self.chart.stacked.dispatch.on('areaClick.toggle', null);

                return self;
            }
        });

        return StackedTrendsView;
    });
