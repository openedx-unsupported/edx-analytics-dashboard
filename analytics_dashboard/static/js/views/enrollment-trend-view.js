define(['d3', 'nvd3', 'utils/utils', 'views/attribute-listener-view'],
    function (d3, nvd3, Utils, AttributeListenerView) {
        'use strict';

        var EnrollmentTrendView = AttributeListenerView.extend({

            initialize: function (options) {
                AttributeListenerView.prototype.initialize.call(this, options);
                var self = this;
                self.renderIfDataAvailable();
            },

            render: function () {
                AttributeListenerView.prototype.render.call(this);
                var self = this,
                    canvas = d3.select(self.el),
                    chart;

                chart = nvd3.models.lineChart()
                    .margin({left: 80, right: 45})  // margins so text fits
                    .showLegend(true)
                    .useInteractiveGuideline(true)
                    .forceY(0)
                    .x(function(d) {
                       // Parse dates to integers
                        return Date.parse(d.date);
                    })
                    .y(function(d) {
                        // Simply return the count
                        return d.count;
                    })
                    .tooltipContent(function (key, y, e, graph) {
                        return '<h3>' + key + '</h3>';
                    });

                chart.xAxis
                    .axisLabel('Date')
                    .tickFormat(function (d) {
                        return Utils.formatDate(d);
                    });

                chart.yAxis.axisLabel('Students');

                // Add the title
                canvas.attr('class', 'line-chart-container')
                    .append('div')
                    .attr('class', 'chart-title')
                    .text(gettext('Daily Student Enrollment'));

                // Append the svg to an inner container so that it adapts to
                // the height of the inner container instead of the outer
                // container which needs to create height for the title.
                canvas.append('div')
                    .attr('class', 'line-chart')
                    .append('svg')
                    .datum([{
                        values: self.model.get(self.modelAttribute),
                        key: gettext('Students')
                    }])
                    .call(chart);

                nv.utils.windowResize(chart.update);

                return this;
            }

        });

        return EnrollmentTrendView;
    }
);
