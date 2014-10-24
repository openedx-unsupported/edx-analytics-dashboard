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
                TrendsView.prototype.render.call(this);

                // Disable expansion of stacked chart datasets
                this.chart.stacked.dispatch.on('areaClick', null);
                this.chart.stacked.dispatch.on('areaClick.toggle', null);

                return this;
            }
        });

        return StackedTrendsView;
    });
