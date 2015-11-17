define(['jquery', 'd3', 'datamaps', 'underscore', 'utils/utils', 'views/attribute-listener-view'],
    function ($, d3, Datamap, _, Utils, AttributeListenerView) {
        'use strict';

        /**
         * This view display a map colored by country count data.  Tooltips and
         * a darker border color will be displayed when the mouse hovers over
         * the country.
         */
        var WorldMapView = AttributeListenerView.extend({

            initialize: function (options) {
                AttributeListenerView.prototype.initialize.call(this, options);
                var self = this;

                // colors can be supplied
                self.options = _.defaults(options, {
                    lowColor: '#bee1f5',
                    highColor: '#124d6f',
                    borderColor: '#ffffff'
                });

                self.renderIfDataAvailable();
            },

            /**
             * Format the data for Datamaps.
             *
             * @returns An object of mappings between country code and value.
             *   ex. { USA: { fillKey: '#f6f6f6', value: 10}, ... }
             */
            formatData: function () {
                var self = this,
                    data = self.model.get(this.options.modelAttribute),
                    formattedData = {};

                // go through all the data and create mappings from country code
                // to value/count
                _(data).each(function (country) {
                    var key = country.countryCode;
                    formattedData[key] = {
                        value: country.count,
                        percent: country.percent,
                        fillKey: key,
                        name: country.countryName
                    };
                });

                return formattedData;
            },

            /**
             * Given a mapping of the country to value, return the mappings of
             * the countries to colors.
             */
            getFills: function (countryData, max) {
                var self = this,
                    fills = {},
                    colorMap;

                colorMap = d3.scale.sqrt()
                    .domain([0, max])
                    .range([self.options.lowColor, self.options.highColor]);

                // create the mapping from country to color
                _(countryData).each(function (countryData, key) {
                    fills[key] = colorMap(countryData.value);
                });

                fills.defaultFill = self.options.lowColor;

                return fills;
            },

            /**
             * Get the maximum value for the set of countries.  The mapping is
             * from formatData().
             */
            getCountryMax: function (countryData) {
                return _(countryData).max(function (countryData) {
                    return countryData.value;
                }).value;
            },

            /**
             * Plugin for the map to display a heatmap legend with labels.
             */
            addHeatmapLegend: function (layer, options) {
                // "this" is the Datamap (not the WorldMapView)
                var self = this,
                    el = self.options.element,
                    canvasHeight = parseInt(d3.select(el).style('height'), 10),
                    swatch = {height: 5, width: 10},
                    margins = {bottom: 10},
                    suggestedTicks = 11,
                    legend,
                    colorMap,
                    ranges;

                colorMap = d3.scale.linear()
                    .range([options.lowColor, options.highColor])
                    .domain([0, options.max]);

                // the rounded evenly spaced intervals
                ranges = colorMap.ticks(suggestedTicks);

                // set up the data (color bands) to display and locations given
                // the provided data
                legend = d3.select(el)
                    .select('.datamap')
                    .append('svg')
                    .attr('class', 'datamaps-legend')
                    .selectAll('svg')
                    .data(ranges.reverse())
                    .enter()
                    .append('g')
                    .attr('class', 'legend')
                    .attr('transform', function (d, i) {
                        // move the legend color swatches to be arranged vertically
                        var x = swatch.width,
                            y = canvasHeight - swatch.height * ranges.length + i * swatch.height - margins.bottom;
                        return 'translate(' + [x, y].join(',') + ')';
                    });

                // display the heatmap
                legend.append('rect')
                    .attr('width', swatch.width)
                    .attr('height', swatch.height)
                    .style('fill', colorMap);

                // display the high and low ranges on the legend
                legend.append('text')
                    .filter(function (d, i) {
                        // only show labels for the bounds
                        return _([0, ranges.length - 1]).contains(i);
                    })
                    .attr('x', swatch.width + 3)
                    .attr('y', swatch.height * 0.75)
                    .attr('dy', '.35em')
                    .text(function (d, i) {
                        var append = '';
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
            popupTemplate: _.template('<div class="hoverinfo"><%=name%>: <%=value%><% if(percent) { %> (<%=percent%>)&rlm;<% } %></div>'),   // jshint ignore:line

            /**
             * Underscore style template for displaying the tooltip for screen
             * readers and in the tooltip icon.
             */
            tooltipTemplate: _.template('<span class="sr-only"><%=text%></span>' +
                '<i class="ico ico-tooltip fa fa-info-circle chart-tooltip" ' +
                'data-toggle="tooltip" data-placement="top" ' +
                'data-track-event="edx.bi.tooltip.displayed" data-track-category="map" ' +
                'title="<%=text%>"></i>'
            ),

            render: function () {
                AttributeListenerView.prototype.render.call(this);
                var self = this,
                    mapData = self.formatData(),
                    max = self.getCountryMax(mapData),
                    fills = self.getFills(mapData, max),
                    borderColor = self.options.borderColor,
                    map,
                    $tooltip;

                // Add the tooltip
                if (_(self.options).has('tooltip')) {
                    $tooltip = $(self.tooltipTemplate({text: self.options.tooltip}));
                    self.$el.append($tooltip);
                    $tooltip.tooltip();
                }

                map = new Datamap({
                    element: self.el,
                    projection: 'equirectangular',
                    geographyConfig: {
                        hideAntarctica: true,
                        borderWidth: 1,
                        borderColor: borderColor,
                        highlightOnHover: true,
                        highlightFillColor: function (geometry) {
                            // keep the fill color the same -- only the border
                            // color will change when hovering
                            return fills[geometry.id] || fills.defaultFill;
                        },
                        highlightBorderColor: d3.rgb(borderColor).darker(1),
                        highlightBorderWidth: 1,
                        popupOnHover: true,
                        popupTemplate: function (geography, data) {
                            return self.popupTemplate({
                                name: data ? data.name : geography.properties.name,
                                value: data ? Utils.localizeNumber(data.value) : 0,
                                percent: data ? Utils.formatDisplayPercentage(data.percent) : 0
                            });
                        }
                    },
                    fills: fills,
                    data: mapData
                });

                // add the legend plugin and render it
                map.addPlugin('heatmapLegend', self.addHeatmapLegend);
                map.heatmapLegend({
                    highColor: self.options.highColor,
                    lowColor: self.options.lowColor,
                    max: max
                });

                return this;
            }
        });

        return WorldMapView;
    }
);
