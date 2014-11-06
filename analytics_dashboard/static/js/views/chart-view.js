/**
 * Abstract class for NVD3 charts.  See TrendsView, HistogramView, and DiscreteBarView.
 */
define(['d3', 'jquery', 'nvd3', 'underscore', 'utils/utils', 'views/attribute-listener-view'],
    function (d3, $, nvd3, _, Utils, AttributeListenerView) {
        'use strict';

        var ChartView = AttributeListenerView.extend({

            defaults: _.extend({}, AttributeListenerView.prototype.defaults, {
                    displayExplicitTicksThreshold: 11,
                    excludeData: [],  // e.g. excludes data rows from chart (e.g. 'Unknown')
                    dataType: 'int',  // e.g. int, percent
                    xAxisMargin: 6,
                    graphShiftSelector: null // Selector used for shifting chart position
                }
            ),

            initialize: function (options) {
                AttributeListenerView.prototype.initialize.call(this, options);
                var self = this;
                self.chart = null;
                self.options = _.extend({}, self.defaults, options);
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

                if (self.options.excludeData.length > 0) {
                    // exclude specific rows of data (e.g. 'Unknown') from display
                    data = _(data).reject(function (datum) {
                        return _(self.options.excludeData).contains(datum[self.options.x.key]);
                    });
                }

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
                    xAxisMargin = this.options.xAxisMargin,
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
                axisEl.attr('transform', 'translate(' + matches[1] + ',' +
                    (parseInt(matches[2], 10) + xAxisMargin) + ')');

                if (this.options.graphShiftSelector) {
                    // Shift the graph down so that it sits flush with the X-axis
                    canvas.select(this.options.graphShiftSelector)
                        .attr('transform', 'translate(' + [0, xAxisMargin].join(',') + ')');
                }
            },

            /**
             * Return the NVD3 chart that will be displayed
             * (e.g. nvd3.models.lineChart).
             */
            getChart: function () {
                throw 'Not implemented';
            },

            /**
             * Returns the formatted label for the x-axis ticks.
             *
             * @param d Data along the x-axis to format.
             */
            formatXTick: function (d) {
                return d;
            },

            parseXData: function (d) {
                var self = this;
                return d[self.options.x.key];
            },

            getExplicitXTicks: function (assembledData) {
                var self = this,
                    xTicks;

                // get dates for the explicit ticks -- assuming data isn't sparse
                xTicks = _(assembledData[0].values).map(function (data) {
                    return self.parseXData(data);
                });

                return xTicks;
            },

            initChart: function (chart) {
                var self = this;

                // minimize the spacing, but leave enough for point at the top to be shown w/o being clipped
                chart.margin({top: self.options.xAxisMargin})
                    .height(300)    // This should be the same as the height set on the chart container in CSS.
                    .forceY(0)
                    .x(function (d) {
                        // Parse dates to integers
                        return self.parseXData(d);
                    })
                    .y(function (d) {
                        // Simply return the count
                        return d[self.options.y.key];
                    });
            },

            getYAxisFormat: function () {
                var self = this,
                    format = d3.format('f');  // defaults to integer

                if (self.options.dataType === 'percent') {
                    format = d3.format('.1%');
                }

                return format;
            },

            /**
             * Different charts have different styled tooltips and different
             * ways to style the tooltip.  This is the template to standardize
             * the style at least.  Views should attach it using its interface.
             */
            hoverTooltipTemplate: _.template(
                    '<table class="nv-pointer-events-none">' +
                    '<thead>' +
                    '<tr class="nv-pointer-events-none">' +
                    '<td class="nv-pointer-events-none" colspan="3"><strong class="x-value">' +
                    '<%=xValue%></strong>' +
                    '</td>' +
                    '</tr>' +
                    '</thead>' +
                    '<tbody>' +
                    '<tr class="nv-pointer-events-none">' +
                    '<td class="legend-color-guide nv-pointer-events-none">' +
                    '<div class="nv-pointer-events-none" style="background-color: <%=swatchColor%>;">' +
                    '</div>' +
                    '</td>' +
                    '<td class="key nv-pointer-events-none"><%=label%></td>' +
                    '<td class="value nv-pointer-events-none"><%=yValue%></td>' +
                    '</tr>' +
                    '</tbody>' +
                    '</table>'
            ),

            render: function () {
                AttributeListenerView.prototype.render.call(this);
                var self = this,
                    canvas = d3.select(self.el),
                    assembledData = self.assembleTrendData();

                self.chart = self.getChart();
                self.initChart(self.chart);

                // explicitly display tick marks for small numbers of points,
                // otherwise ticks will be interpolated and labels look to be
                // repeated on the x-axis
                if (!_(self.options).isUndefined('displayExplicitTicksThreshold')) {
                    if (self.model.get(
                        self.options.modelAttribute).length < self.options.displayExplicitTicksThreshold) {
                        // get dates for the explicit ticks -- assuming data isn't sparse
                        self.chart.xAxis.tickValues(self.getExplicitXTicks(assembledData));
                    }
                }

                self.chart.xAxis.tickFormat(self.formatXTick);

                self.chart.yAxis
                    .showMaxMin(false)
                    .tickFormat(Utils.localizeNumber);
                self.chart.yAxis.tickFormat(self.getYAxisFormat());

                // Append the svg to an inner container so that it adapts to
                // the height of the inner container instead of the outer
                // container which needs to create height for the title.
                canvas.append('svg')
                    .datum(assembledData)
                    .call(self.chart);

                self.styleChart();

                nvd3.utils.windowResize(function () {
                    self.chart.update();
                    self.styleChart();
                });

                return this;
            }

        });

        return ChartView;
    }
);
