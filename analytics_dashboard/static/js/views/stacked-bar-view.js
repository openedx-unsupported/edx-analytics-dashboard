define(
  ['d3', 'nvd3', 'underscore', 'views/discrete-bar-view'],
  (d3, nvd3, _, DiscreteBarView) => {
    'use strict';

    const StackedBarView = DiscreteBarView.extend({

      defaults: _.extend({}, DiscreteBarView.prototype.defaults, {
        barSelector: '.nv-bar',
        truncateXTicks: true,
        interactiveTooltipValueTemplate(trend) {
          /* Translators: <%=value%> will be replaced by a number followed by a percentage.
                         For example, "400 (29%)" */
          return _.template(gettext('<%=value%> (<%=percent%>)'))({
            value: trend.value,
            percent: d3.format('.1%')(trend.point[trend.options.percent_key]),
          });
        },
        click(d) {
          if (_(d).has('url')) {
            document.location.href = d.url;
          }
        },
        x: { key: 'id', displayKey: 'name' },
        y: { key: 'count' },
      }),

      getChart() {
        return nvd3.models.multiBarChart();
      },

      initChart(chart) {
        const self = this;
        DiscreteBarView.prototype.initChart.call(self, chart);

        chart.stacked(true)
          .showControls(false)
          .showLegend(false)
          .reduceXTicks(false); // shows all ticks

        chart.tooltip.contentGenerator((o) => {
          const tips = [];
          _(self.options.trends).each((trend) => {
            tips.push(self.buildTrendTip(trend, o));
          });

          return self.hoverTooltipTemplate({
            xValue: self.buildTipHeading(o.data),
            tips,
          });
        });
      },

    });

    return StackedBarView;
  },
);
