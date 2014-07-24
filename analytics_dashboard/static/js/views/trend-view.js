define(['jquery', 'backbone', 'highcharts'],
    function ($, Backbone, highcharts) {
        'use strict';

        var TrendView = Backbone.View.extend({

            // Renders the view's template to the UI
            render: function () {
                var self = this,
                    series;

                series = self.model.getEnrollmentSeries();

                self.$el.highcharts({
                    credits: {
                        enabled: false
                    },
                    chart: {
                        zoomType: 'x'
                    },
                    title: {
                        text: 'Daily Student Enrollment',
                    },
                    xAxis: {
                        type: 'datetime',
                        labels: {
                            formatter: function () {
                                return highcharts.dateFormat('%b %e, %Y', this.value);
                            }
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Students'
                        }
                    },
                    legend: {
                        enabled: false
                    },
                    series: [
                        {
                            name: 'Students',
                            data: series
                        }
                    ]
                });

                return self;
            }

        });

        return TrendView;
    }
);
