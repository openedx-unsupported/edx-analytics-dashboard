define(['d3', 'nvd3', 'underscore', 'views/discrete-bar-view'],
    function (d3, nvd3, _, DiscreteBarView) {
        'use strict';

        var StackedBarView = DiscreteBarView.extend({

            defaults: _.extend({}, DiscreteBarView.prototype.defaults, {
                    barSelector: '.nv-bar',
                    truncateXTicks: true,
                    interactiveTooltipValueTemplate: function (trend) {
                        /* Translators: <%=value%> will be replaced by a number followed by a percentage.
                         For example, "400 (29%)" */
                        return _.template(gettext('<%=value%> (<%=percent%>)'))({
                            value: trend.value,
                            percent: d3.format('.1%')(trend.point[trend.options.percent_key])
                        });
                    },
                    click: function (d) {
                        if (_(d).has('url')) {
                            document.location.href = d.url;
                        }
                    },
                    x: {key: 'id', displayKey: 'name'},
                    y: {key: 'count'}
                }
            ),

            getChart: function () {
                return nvd3.models.multiBarChart();
            },

            initChart: function (chart) {
                var self = this;
                DiscreteBarView.prototype.initChart.call(self, chart);

                chart.stacked(true)
                    .showControls(false)
                    .showLegend(false)
                    .reduceXTicks(false);  // shows all ticks

                chart.tooltipContent(function(key, x, y, e) {
                    var tips = [];
                    _(self.options.trends).each(function(trend) {
                        var trendY = self.getYAxisFormat()(e.point[trend.key]);
                        tips.push(self.buildTrendTip(trend, x, trendY, e));
                    });

                    return self.hoverTooltipTemplate({
                        xValue: self.buildTipHeading(e.point),
                        tips: tips
                    });
                });
            }

        });

        return StackedBarView;
    });
