define(
  ['jquery', 'd3', 'datamaps', 'underscore', 'utils/utils', 'views/attribute-listener-view'],
  ($, d3, Datamap, _, Utils, AttributeListenerView) => {
    'use strict';

    /**
         * This view display a map colored by country count data.  Tooltips and
         * a darker border color will be displayed when the mouse hovers over
         * the country.
         */
    const WorldMapView = AttributeListenerView.extend({

      initialize(options) {
        const self = this;
        AttributeListenerView.prototype.initialize.call(this, options);

        // colors can be supplied
        self.options = _.defaults(options, {
          lowColor: '#bee1f5',
          highColor: '#124d6f',
          borderColor: '#ffffff',
        });
      },

      /**
             * Format the data for Datamaps.
             *
             * @returns An object of mappings between country code and value.
             *   ex. { USA: { fillKey: '#f6f6f6', value: 10}, ... }
             */
      formatData() {
        const self = this;
        const data = self.model.get(this.options.modelAttribute);
        const formattedData = {};

        // go through all the data and create mappings from country code
        // to value/count
        _(data).each((country) => {
          const key = country.countryCode;
          formattedData[key] = {
            value: country.count,
            percent: country.percent,
            fillKey: key,
            name: country.countryName,
          };
        });

        return formattedData;
      },

      /**
             * Given a mapping of the country to value, return the mappings of
             * the countries to colors.
             */
      getFills(countryData, max) {
        const self = this;
        const fills = {};

        const colorMap = d3.scale.sqrt()
          .domain([0, max])
          .range([self.options.lowColor, self.options.highColor]);

        // create the mapping from country to color
        _(countryData).each((country, key) => {
          fills[key] = colorMap(country.value);
        });

        fills.defaultFill = self.options.lowColor;

        return fills;
      },

      /**
             * Get the maximum value for the set of countries.  The mapping is
             * from formatData().
             */
      getCountryMax(countryData) {
        return _(countryData).max((country) => country.value).value;
      },

      /**
             * Plugin for the map to display a heatmap legend with labels.
             */
      addHeatmapLegend(layer, options) {
        // "this" is the Datamap (not the WorldMapView)
        const self = this;
        const el = self.options.element;
        const canvasHeight = parseInt(d3.select(el).style('height'), 10);
        const swatch = { height: 5, width: 10 };
        const margins = { bottom: 10 };
        const suggestedTicks = 11;

        const colorMap = d3.scale.linear()
          .range([options.lowColor, options.highColor])
          .domain([0, options.max]);

        // the rounded evenly spaced intervals
        const ranges = colorMap.ticks(suggestedTicks);

        // set up the data (color bands) to display and locations given
        // the provided data
        const legend = d3.select(el)
          .select('.datamap')
          .append('svg')
          .attr('class', 'datamaps-legend')
          .selectAll('svg')
          .data(ranges.reverse())
          .enter()
          .append('g')
          .attr('class', 'legend')
          .attr('transform', (d, i) => {
            // move the legend color swatches to be arranged vertically
            const x = swatch.width;
            const y = ((canvasHeight - (swatch.height * ranges.length))
                                + (i * swatch.height)) - margins.bottom;
            return `translate(${[x, y].join(',')})`;
          });

        // display the heatmap
        legend.append('rect')
          .attr('width', swatch.width)
          .attr('height', swatch.height)
          .style('fill', colorMap);

        // display the high and low ranges on the legend
        legend.append('text')
          .filter((d, i) => _([0, ranges.length - 1]).contains(i)) // only show labels for the bounds
          .attr('x', swatch.width + 3)
          .attr('y', swatch.height * 0.75)
          .attr('dy', '.35em')
          .text((d, i) => {
            let append = '';
            // ticks are rounded, so denote this in our legend
            if (i === 0) {
              append = '+';
            }
            return d.toLocaleString() + append;
          });
      },

      /**
             * Underscore style template for the hover popup that displays a
             * label/name and value.
             */
      // See http://www.w3.org/TR/WCAG20-TECHS/H34.html for info on &rlm;
      // eslint-disable-next-line max-len
      popupTemplate: _.template('<div class="hoverinfo"><%=name%>: <%=value%><% if(percent) { %> (<%=percent%>)&rlm;<% } %></div>'),

      /**
             * Underscore style template for displaying the tooltip for screen
             * readers and in the tooltip icon.
             */
      tooltipTemplate: _.template('<span class="sr-only"><%=text%></span>'
                + '<span class="ico ico-tooltip fa fa-info-circle chart-tooltip" '
                + 'data-toggle="tooltip" data-placement="top" data-track-type="tooltip"'
                + 'data-track-event="edx.bi.tooltip.displayed" data-track-category="map" '
                + 'title="<%=text%>" aria-hidden="true"></span>'),

      render() {
        const self = this;
        let $tooltip;

        AttributeListenerView.prototype.render.call(this);
        const mapData = self.formatData();
        const max = self.getCountryMax(mapData);
        const fills = self.getFills(mapData, max);
        const { borderColor } = self.options;

        // Add the tooltip
        if (_(self.options).has('tooltip')) {
          $tooltip = $(self.tooltipTemplate({ text: self.options.tooltip }));
          self.$el.append($tooltip);
          $tooltip.tooltip();
        }

        const map = new Datamap({
          element: self.el,
          height: $('.section-data-viz').height(),
          responsive: true,
          projection: 'equirectangular',
          geographyConfig: {
            hideAntarctica: true,
            borderWidth: 1,
            borderColor,
            highlightOnHover: true,
            highlightFillColor(geometry) {
              // keep the fill color the same -- only the border
              // color will change when hovering
              return fills[geometry.id] || fills.defaultFill;
            },
            highlightBorderColor: d3.rgb(borderColor).darker(1),
            highlightBorderWidth: 1,
            popupOnHover: true,
            popupTemplate(geography, data) {
              return self.popupTemplate({
                name: data ? data.name : geography.properties.name,
                value: data ? Utils.localizeNumber(data.value) : 0,
                percent: data ? Utils.formatDisplayPercentage(data.percent) : 0,
              });
            },
          },
          fills,
          data: mapData,
        });

        // add the legend plugin and render it
        map.addPlugin('heatmapLegend', self.addHeatmapLegend);
        map.heatmapLegend({
          highColor: self.options.highColor,
          lowColor: self.options.lowColor,
          max,
        });

        // Scale the map on window resize to be responsive.
        $(window).on('resize', () => {
          map.resize();
          $('svg.datamaps-legend').remove();
          map.heatmapLegend({
            highColor: self.options.highColor,
            lowColor: self.options.lowColor,
            max,
          });
        });

        return this;
      },
    });

    return WorldMapView;
  },
);
