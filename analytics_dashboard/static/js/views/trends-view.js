define(['bootstrap', 'd3', 'jquery', 'nvd3', 'underscore', 'utils/utils', 'views/attribute-listener-view'],
    function (bootstrap, d3, $, nvd3, _, Utils, AttributeListenerView) {
        'use strict';

        var TrendsView = AttributeListenerView.extend({

            initialize: function (options) {
                AttributeListenerView.prototype.initialize.call(this, options);
                var self = this;
                self.options = options;
                self.renderIfDataAvailable();
            },

            /**
             * Returns an array of maps of the trend data passed to nvd3 for
             * rendering.  The map consists of the trend data as 'values' and
             * the trend title as 'key'.
             */
            assembleTrendData: function() {
                var self = this,
                    combinedTrends,
                    data = self.model.get(self.options.modelAttribute),
                    trendOptions = self.options.trends;

                // parse and format the data for nvd3
                combinedTrends = _(trendOptions).map( function (trendOption) {
                    var values = _(data).map(function (datum) {
                        var keyedValue = {},
                            yKey = trendOption.key || self.options.y.key;
                        keyedValue[self.options.y.key] = datum[yKey];
                        keyedValue[self.options.x.key] = datum[self.options.x.key];
                        return keyedValue;
                    });

                    return {
                        values: values,
                        // displayed trend label/title
                        key: trendOption.title,
                        // default color used if none specified
                        color: trendOption.color || undefined
                    };
                });

                return combinedTrends;
            },

            render: function () {
                AttributeListenerView.prototype.render.call(this);
                var self = this,
                    canvas = d3.select(self.el),
                    tooltipTemplate = _.template('<i class="ico ico-tooltip fa fa-info-circle chart-tooltip" data-toggle="tooltip" data-placement="top" title="<%=text%>"></i>'),
                    chart,
                    title,
                    $tooltip;

                chart = nvd3.models.lineChart()
                    .margin({left: 80, right: 65})  // margins so text fits
                    .showLegend(true)
                    .useInteractiveGuideline(true)
                    .forceY(0)
                    .x(function (d) {
                        // Parse dates to integers
                        return Date.parse(d[self.options.x.key]);
                    })
                    .y(function (d) {
                        // Simply return the count
                        return d[self.options.y.key];
                    })
                    .tooltipContent(function (key, y, e, graph) {
                        return '<h3>' + key + '</h3>';
                    });

                chart.xAxis
                    .axisLabel(self.options.x.title)
                    .tickFormat(function (d) {
                        return Utils.formatDate(d);
                    });

                chart.yAxis.axisLabel(self.options.y.title);

                title = canvas.attr('class', 'line-chart-container')
                    .append('div')
                    .attr('class', 'chart-title')
                    .text(self.options.title);

                // Add the tooltip
                if(_(self.options).has('tooltip')) {
                    $tooltip = $(tooltipTemplate({text: self.options.tooltip}));
                    $(title[0]).append($tooltip);
                    $tooltip.tooltip();
                }

                // Append the svg to an inner container so that it adapts to
                // the height of the inner container instead of the outer
                // container which needs to create height for the title.
                canvas.append('div')
                    .attr('class', 'line-chart')
                    .append('svg')
                    .datum(self.assembleTrendData())
                    .call(chart);

                nvd3.utils.windowResize(chart.update);

                return this;
            }

        });

        return TrendsView;
    }
);
