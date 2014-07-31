define(['highcharts', 'jquery', 'views/simple-model-attribute-view'],
    function (highcharts, $, SimpleModelAttributeView) {
        'use strict';

        var EnrollmentTrendView = SimpleModelAttributeView.extend({
            /**
             * Convert string to UTC timestamp
             *
             * @param date
             * @returns {number}
             * @private
             */
            _convertDate: function (date) {
                var tokens = date.split('-');
                // JS months start at 0
                return Date.UTC(tokens[0], tokens[1] - 1, tokens[2]);
            },

            /**
             * Convert the array of Objects received from the server to a Array<Array<date, int>>
             *
             * @param data
             * @returns {*}
             * @private
             */
            _formatData: function (data) {
                return _.map(data, function (datum) {
                    return [this._convertDate(datum.date), datum.count];
                }, this);
            },

            render: function () {
                var series = this._formatData(this.model.get(this.modelAttribute));

                this.$el.highcharts({
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

                return this;
            }

        });

        return EnrollmentTrendView;
    }
);
