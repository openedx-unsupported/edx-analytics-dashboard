/**
 * Abstract class for NVD3 charts.  See TrendsView, HistogramView, and DiscreteBarView.
 */
define(
  ['d3', 'jquery', 'nvd3', 'underscore', 'utils/utils', 'views/attribute-listener-view'],
  (d3, $, nvd3, _, Utils, AttributeListenerView) => {
    'use strict';

    const ChartView = AttributeListenerView.extend({

      defaults: _.extend({}, AttributeListenerView.prototype.defaults, {
        displayExplicitTicksThreshold: 11,
        excludeData: [], // e.g. excludes data rows from chart (e.g. 'Unknown')
        dataType: 'int', // e.g. int, percent
        xAxisMargin: 6,
        graphShiftSelector: null, // Selector used for shifting chart position
        truncateXTicks: false, // Determines if x axis ticks should be truncated
      }),

      /**
             * Initializes a ChartView.
             *
             * @param options (Object) an object specifying view parameters.
             * This options hash must include:
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
      initialize(options) {
        const self = this;
        AttributeListenerView.prototype.initialize.call(this, options);
        self.chart = null;
        self.options = _.extend({}, self.defaults, options);
        _.bindAll(this, 'truncateXTick', 'formatXTick');
      },

      /**
             * Returns an array of maps of the trend data passed to nvd3 for
             * rendering.  The map consists of the trend data as 'values' and
             * the trend title as 'key'.
             *
             * Part of the contract is that
             * 'this.model.get(this.options.modelAttribute)' has a particular
             * structure: it is an array of objects, where each object
             * represents a tick in the chart.  Each object contains key/value
             * pairs for each trend as well as a key/value pair which maps the x
             * axis name to the value for that particular tick.  For example:
             *   this.options.modelAttribute -> [
             *       {
             *           day: '2000-01-01', // the x-axis in this example
             *           someTrend: 4,      // a trend value
             *           anotherTrend: 22   // another trend value
             *       },
             *       ...
             *   ]
             */
      assembleTrendData() {
        const self = this;
        let data = self.model.get(self.options.modelAttribute);
        const trendOptions = self.options.trends;

        if (self.options.excludeData.length > 0) {
          // exclude specific rows of data (e.g. 'Unknown') from display
          data = _(data).reject((datum) => _(self.options.excludeData).contains(datum[self.options.x.key]));
        }

        // parse and format the data for nvd3
        const combinedTrends = _(trendOptions).map((trendOption) => {
          const values = _(data).map((datum) => {
            const keyedValue = _(datum).clone();
            const yKey = trendOption.key || self.options.y.key;
            keyedValue[self.options.y.key] = datum[yKey];
            keyedValue[self.options.x.key] = datum[self.options.x.key];
            return keyedValue;
          });

          return {
            values,
            // displayed trend label/title
            key: trendOption.title,
            // default color used if none specified
            color: trendOption.color || undefined,
          };
        });

        return combinedTrends;
      },

      /**
             * If option x.displayKey is provided, build a mapping from the key
             * to the display name.  E.g.: x: {key: 'id', displayKey: 'name'}.
             * This can be useful if the dataset has unique identifiers that
             * aren't display friendly.
             */
      buildXLabelMapping() {
        const self = this;
        const data = self.model.get(self.options.modelAttribute);
        let mapping;

        if (_(self.options.x).has('displayKey')) {
          mapping = _.object(_(data).pluck(self.options.x.key), _(data).pluck(self.options.x.displayKey));
        }

        return mapping;
      },

      styleChart() {
        const self = this;
        const canvas = d3.select(self.el);
        // ex. translate(200, 200) or translate(200 200)
        const translateRegex = /translate\((\d+)[,\s]\s*(\d+)\)/g;
        const { xAxisMargin } = self.options;

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
        const axisEl = canvas.select('.nvd3 .nv-axis.nv-x');
        const matches = translateRegex.exec(axisEl.attr('transform'));
        axisEl.attr('transform', `translate(${matches[1]},${
          parseInt(matches[2], 10) + xAxisMargin})`);

        if (self.options.graphShiftSelector) {
          // Shift the graph down so that it sits flush with the X-axis
          canvas.select(self.options.graphShiftSelector)
            .attr('transform', `translate(${[0, xAxisMargin].join(',')})`);
        }
      },

      /**
             * Return the NVD3 chart that will be displayed
             * (e.g. nvd3.models.lineChart).
             */
      getChart() {
        throw 'Not implemented'; // eslint-disable-line no-throw-literal
      },

      /**
             * Returns the formatted label for the x-axis ticks.
             *
             * @param d Data along the x-axis to format.
             */
      formatXTick(d) {
        const self = this;
        let label = d;
        if (_(self).has('xLabelMapping') && _(self.xLabelMapping).has(d)) {
          label = self.xLabelMapping[d];
        }
        return label;
      },

      /**
            * Truncate (e.g. add ellipses) long labels shown beneath the bar.
            */
      truncateXTick() {
        throw 'Not implemented'; // eslint-disable-line no-throw-literal
      },

      parseXData(d) {
        const self = this;
        return d[self.options.x.key];
      },

      getExplicitXTicks(assembledData) {
        const self = this;

        // get dates for the explicit ticks -- assuming data isn't sparse
        const xTicks = _(assembledData[0].values).map((data) => self.parseXData(data));

        return xTicks;
      },

      initChart(chart) {
        const self = this;

        // minimize the spacing, but leave enough for point at the top to be shown w/o being clipped
        chart.margin({ top: self.options.xAxisMargin, right: 60 })
          .height(300) // This should be the same as the height set on the chart container in CSS.
          .forceY(0)
          .x((d) => self.parseXData(d)) // Parse dates to integers
          .y((d) => d[self.options.y.key]).legend.maxKeyLength(25); // Simply return the count
      },

      getYAxisFormat() {
        const self = this;
        let format = d3.format('f'); // defaults to integer

        if (self.options.dataType === 'percent') {
          format = d3.format('.1%');
        } else if (self.options.dataType === 'decimal') {
          format = d3.format('.1f');
        }

        return format;
      },

      /**
             * Different charts have different styled tooltips and different
             * ways to style the tooltip.  This is the template to standardize
             * the style at least.  Views should attach it using its interface.
             */
      hoverTooltipTemplate: _.template(
        '<table class="nv-pointer-events-none">'
                    + '<thead>'
                    + '<tr class="nv-pointer-events-none">'
                    + '<td class="nv-pointer-events-none" colspan="3"><strong class="x-value">'
                    + '<%=xValue%></strong>'
                    + '</td>'
                    + '</tr>'
                    + '</thead>'
                    + '<tbody>'
                    + '<% _.each(tips, function(tip) { %>'
                    + '<tr class="nv-pointer-events-none">'
                    + '<td class="legend-color-guide nv-pointer-events-none">'
                    + '<div class="nv-pointer-events-none" style="background-color: <%=tip.color%>;">'
                    + '</div>'
                    + '</td>'
                    + '<td class="key nv-pointer-events-none"><%=tip.label%></td>'
                    + '<td class="value nv-pointer-events-none"><%=tip.value%></td>'
                    + '</tr>'
                    + '<% }); %>'
                    + '</tbody>'
                    + '</table>',
      ),

      /**
             * Implement this to enable users to click on chart elements.  This
             * is called when render is complete and the click option is specified.
             */
      addChartClick() {
        throw 'Not implemented'; // eslint-disable-line no-throw-literal
      },

      render() {
        const self = this;
        AttributeListenerView.prototype.render.call(this);
        const canvas = d3.select(self.el);
        const assembledData = self.assembleTrendData();
        const xLabelMapping = self.buildXLabelMapping();

        self.xLabelMapping = xLabelMapping;
        self.chart = self.getChart();
        self.initChart(self.chart);

        // explicitly display tick marks for small numbers of points,
        // otherwise ticks will be interpolated and labels look to be
        // repeated on the x-axis
        if (!_(self.options).isUndefined('displayExplicitTicksThreshold')) {
          if (self.model.get(
            self.options.modelAttribute,
          ).length < self.options.displayExplicitTicksThreshold) {
            // get dates for the explicit ticks -- assuming data isn't sparse
            self.chart.xAxis.tickValues(self.getExplicitXTicks(assembledData));
          }
        }

        self.chart.xAxis.tickFormat(self.options.truncateXTicks ? self.truncateXTick : self.formatXTick);

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

        nvd3.utils.windowResize(() => {
          self.chart.update();
          self.styleChart();
        });

        if (_(self.options.click).isFunction()) {
          self.addChartClick();
        }

        return self;
      },

    });

    return ChartView;
  },
);
