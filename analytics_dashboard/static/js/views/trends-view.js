define(['bootstrap', 'd3', 'jquery', 'moment', 'nvd3', 'underscore', 'views/attribute-listener-view'],
    function (bootstrap, d3, $, moment, nvd3, _, AttributeListenerView) {
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
            assembleTrendData: function () {
                var self = this,
                    combinedTrends,
                    data = self.model.get(self.options.modelAttribute),
                    trendOptions = self.options.trends;

                // parse and format the data for nvd3
                combinedTrends = _(trendOptions).map(function (trendOption) {
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

            styleChart: function () {
                var canvas = d3.select(this.el),
                    // ex. translate(200, 200) or translate(200 200)
                    translateRegex = /translate\((\d+)[,\s]\s*(\d+)\)/g,
                    xAxisMargin = 6,
                    axisEl,
                    matches;

                // Add background to X-axis
                canvas.select('.nv-x.nv-axis')
                    .insert('rect', 'g')
                    .attr('transform', 'translate(-60, 0)')
                    .attr('class', 'x-axis-background')
                    // TODO Fix height/overflow issue. If height set to 100%, rect overflows. Height should
                    // not be hardcoded.
                    .attr('height', '21px')
                    .attr('width', '100%');

                // Remove the border on the Y-axis
                canvas.select('.nv-y path.domain').remove();

                // Remove the grid lines
                canvas.selectAll('.nvd3 .nv-axis line').remove();

                // Remove max value from the X-axis
                canvas.select('.nvd3 .nv-axis.nv-x .nv-axisMaxMin:nth-child(3)').remove();

                // Get the existing X-axis translation and shift it down a few more pixels.
                axisEl = canvas.select('.nvd3 .nv-axis.nv-x');
                matches = translateRegex.exec(axisEl.attr('transform'));
                axisEl.attr('transform', 'translate(' + matches[1] + ',' + (parseInt(matches[2], 10) + xAxisMargin) + ')');
            },

            /**
             * Underscore style template for displaying the tooltip for screen
             * readers and in the tooltip icon.
             */
            tooltipTemplate: _.template('<span class="sr-only"><%=text%></span>' +
                '<i class="ico ico-tooltip fa fa-info-circle chart-tooltip" data-toggle="tooltip" data-placement="top" title="<%=text%>"></i>'),

            render: function () {
                AttributeListenerView.prototype.render.call(this);
                var self = this,
                    canvas = d3.select(self.el),
                    chart,
                    $tooltip;

                chart = nvd3.models.lineChart()
                    .margin({top: 1})
                    .height(300)    // This should be the same as the height set on the chart container in CSS.
                    .showLegend(false)
                    .useInteractiveGuideline(true)
                    .forceY(0)
                    .x(function (d) {
                        // Parse dates to integers
                        return Date.parse(d[self.options.x.key]);
                    })
                    .y(function (d) {
                        // Simply return the count
                        return d[self.options.y.key];
                    });

                chart.xAxis
                    .tickFormat(function (d) {
                        // date is converted to unix timestamp from our original mm-dd-yyyy format
                        // and setting the timezone to gmt displays the correct date
                        return moment(d).zone('+0000').format('M/D');
                    });

                chart.yAxis.showMaxMin(false);

                // Add the tooltip
                if (_(self.options).has('tooltip')) {
                    $tooltip = $(self.tooltipTemplate({text: self.options.tooltip}));
                    $(canvas[0]).append($tooltip);
                    $tooltip.tooltip();
                }

                // Append the svg to an inner container so that it adapts to
                // the height of the inner container instead of the outer
                // container which needs to create height for the title.
                canvas.attr('class', 'line-chart-container')
                    .append('div')
                    .attr('class', 'line-chart')
                    .append('svg')
                    .datum(self.assembleTrendData())
                    .call(chart);

                self.styleChart();

                nvd3.utils.windowResize(chart.update);
                nv.utils.windowResize(function () {
                    self.styleChart();
                });

                return this;
            }

        });

        return TrendsView;
    }
);
