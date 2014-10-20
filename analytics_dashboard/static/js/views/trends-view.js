define(['bootstrap', 'd3', 'jquery', 'moment', 'nvd3', 'underscore', 'utils/utils', 'views/attribute-listener-view'],
    function (bootstrap, d3, $, moment, nvd3, _, Utils, AttributeListenerView) {
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
                    data = self.model.get(self.options.modelAttribute),
                    trendOptions = self.options.trends,
                    combinedTrends;

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

                // Get the existing X-axis translation and shift it down a few more pixels.
                axisEl = canvas.select('.nvd3 .nv-axis.nv-x');
                matches = translateRegex.exec(axisEl.attr('transform'));
                axisEl.attr('transform',
                        'translate(' + matches[1] + ',' + (parseInt(matches[2], 10) + xAxisMargin) + ')');
            },

            /**
             * Underscore style template for displaying the tooltip for screen
             * readers and in the tooltip icon.
             */
            tooltipTemplate: _.template('<span class="sr-only"><%=text%></span>' +
                '<i class="ico ico-tooltip fa fa-info-circle chart-tooltip" ' +
                'data-toggle="tooltip" data-placement="top" ' +
                'data-track-event="edx.bi.tooltip.displayed" data-track-category="trend" ' +
                'title="<%=text%>"></i>'
            ),

            render: function () {
                AttributeListenerView.prototype.render.call(this);
                var self = this,
                    canvas = d3.select(self.el),
                    assembledData = self.assembleTrendData(),
                    displayExplicitTicksThreshold = 11,
                    chart,
                    $tooltip,
                    xTicks;

                chart = nvd3.models.lineChart()
                    // minimize the spacing, but leave enough for point at the top to be shown w/o being clipped
                    .margin({top: 6})
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

                // explicitly display tick marks for small numbers of points, otherwise
                // ticks will be interpolated and dates look to be repeated on the x-axis
                if (self.model.get(self.options.modelAttribute).length < displayExplicitTicksThreshold) {
                    // get dates for the explicit ticks -- assuming data isn't sparse
                    xTicks = _(self.assembleTrendData()[0].values).map(function (data) {
                        return Date.parse(data[self.options.x.key]);
                    });
                    chart.xAxis.tickValues(xTicks);
                }

                chart.xAxis
                    .tickFormat(function (d) {
                        // date is converted to unix timestamp from our original mm-dd-yyyy format
                        // and setting the timezone to gmt displays the correct date
                        return moment(d).zone('+0000').format('M/D');
                    });

                chart.yAxis
                    .showMaxMin(false)
                    .tickFormat(Utils.localizeNumber);

                if (_(self.options).has('interactiveTooltipHeader')) {
                    chart.interactiveLayer.tooltip.headerFormatter(function (d) {
                        return interpolate(self.options.interactiveTooltipHeader, {value: d}, true);    // jshint ignore:line
                    });
                }

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
                    .datum(assembledData)
                    .call(chart);

                self.styleChart();

                nvd3.utils.windowResize(chart.update);
                nvd3.utils.windowResize(function () {
                    self.styleChart();
                });

                return this;
            }

        });

        return TrendsView;
    }
);
