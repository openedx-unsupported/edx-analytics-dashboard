/**
 * Abstract class for NVD3 bar charts (includes discrete bar and histogram).
 */
define(
  ['d3', 'nvd3', 'underscore', 'utils/utils', 'views/chart-view'],
  (d3, nvd3, _, Utils, ChartView) => {
    'use strict';

    const BarView = ChartView.extend({

      defaults: _.extend({}, ChartView.prototype.defaults, {
        graphShiftSelector: '.nv-barsWrap',
        tipCharLimit: 250, // clip and add ellipses to long tooltips
        barSelector: '.nv-bar',
      }),

      /**
             * Returns the x-value/label displayed on the chart.  Further formatting (e.g. adding ellipse)
             * should be done in formatXTick (see DiscreteBarView) for labels beneath the bars.
             *
             * This is called for both display labels beneath the bars and in tooltips.
             */
      formatXValue(xValue) {
        const self = this;
        const trend = self.options.trends[0];
        const { maxNumber } = trend;
        let formattedXValue = ChartView.prototype.formatXTick.call(self, xValue);

        if (!_(maxNumber).isUndefined()) {
          // e.g. 100+
          formattedXValue = formattedXValue >= maxNumber ? `${maxNumber}+` : formattedXValue;
        }

        return formattedXValue;
      },

      /**
             * Returns function for displaying a truncated label.
             */
      truncateXTick(d) {
        const self = this;
        const x = self.formatXValue(d);
        const barWidth = d3.select(self.options.barSelector).attr('width');
        // this is a rough estimate of how wide a character is
        const charWidth = 6;
        const characterLimit = Math.floor(barWidth / charWidth);
        let formattedLabel = x;

        if (characterLimit < 3) {
          // no labels will be displayed if label space is limited
          formattedLabel = '';
        } else if (_(formattedLabel).size() > characterLimit) {
          formattedLabel = Utils.truncateText(x, characterLimit);
        }

        return formattedLabel;
      },

      addChartClick() {
        const self = this;
        d3.selectAll('rect.nv-bar')
          .style('cursor', 'pointer')
          .on('click', (d) => {
            self.options.click(d);
          });
      },

      buildTrendTip(trend, o) {
        const self = this;
        let swatchColor = trend.color; // e.g #ff9988 or a function
        let label = trend.title; // e.g. 'my title' or a function
        const key = trend.key ? trend.key : self.options.y.key;
        let yValue = self.getYAxisFormat()(o.data[key]);

        // bar colors can be dynamically assigned based on value
        if (_(swatchColor).isFunction()) {
          swatchColor = trend.color(o.index);
        } else {
          swatchColor = trend.color;
        }

        // bar label can be dynamically assigned based on value
        if (_(label).isFunction()) {
          label = trend.title(o.index);
        } else {
          label = trend.title;
        }

        if (_(self.options).has('interactiveTooltipValueTemplate')) {
          yValue = self.options.interactiveTooltipValueTemplate({ value: yValue, point: o.data, options: trend });
        }

        return {
          label,
          color: swatchColor,
          value: yValue,
        };
      },

      /**
             * Builds the header for the interactive tooltip.
             */
      buildTipHeading(point) {
        const self = this;
        let heading = self.formatXValue(point[self.options.x.key]);
        const charLimit = self.options.tipCharLimit;

        // create the tooltip when hovering over a bar
        if (_(self.options).has('interactiveTooltipHeaderTemplate')) {
          if (_(self.options).has('tipCharLimit')) {
            // truncate long labels in the tooltips
            if (_(heading).size() > charLimit) {
              heading = Utils.truncateText(heading, charLimit);
            }
          }
          heading = self.options.interactiveTooltipHeaderTemplate({ value: heading });
        }
        return heading;
      },

      initChart(chart) {
        const self = this;
        ChartView.prototype.initChart.call(self, chart);

        // NVD3's bar views display tooltips differently than for graphs
        chart.tooltip.contentGenerator((o) => {
          const trend = self.options.trends[o.data.series];
          // 'e' contains the raw x-value and 'x' could be formatted (e.g. truncated, ellipse, etc.)
          const tips = [self.buildTrendTip(trend, o)];

          return self.hoverTooltipTemplate({
            xValue: self.buildTipHeading(o.data),
            tips,
          });
        });
      },
    });

    return BarView;
  },
);
