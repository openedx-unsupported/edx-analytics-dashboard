define(['jquery', 'backbone', 'highcharts', 'models/course-model'],
    function($, Backbone, highcharts, CourseModel){
        'use strict';

        var TrendView = Backbone.View.extend({

            // Renders the view's template to the UI
            render: function() {
                var self = this,
                    series;

                series = self.model.getEnrollmentSeries();

                $(self.el).highcharts({
                    credits: {
                        enabled: false
                    },
                    chart: {
                        zoomType: 'x'
                    },
                    title: {
                        text: 'Total Daily Student Enrollment',
                        x: -20 //center
                    },
                    subtitle: {
                        text: ' ',
                        x: -20
                    },
                    xAxis: {
                        type: 'datetime',
                        labels: {
                            formatter: function() {
                                return highcharts.dateFormat('%b %e, %Y',
                                    this.value);
                            }
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Student Enrollment'
                        },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'middle',
                        borderWidth: 0
                    },
                    series: [{
                        name: 'Enrolled Students',
                        data: series
                    }]
                });
                return self;
            }

        });

        return TrendView;
    }
);