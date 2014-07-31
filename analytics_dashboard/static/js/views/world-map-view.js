define(['highchartsMapWorld', 'jquery', 'views/simple-model-attribute-view'],
    function (maps, $, SimpleModelAttributeView) {
        'use strict';

        var WorldMapView = SimpleModelAttributeView.extend({
            render: function () {
                var title = this.$el.data('title');
                var seriesName = this.$el.data('series-name');
                var seriesData = this.model.get(this.modelAttribute).slice(0); // Clone the array to avoid issues with other consumers

                this.$el.highcharts('Map', {
                    title: { text: title },
                    mapNavigation: {
                        enabled: true,
                        buttonOptions: {
                            verticalAlign: 'bottom'
                        }
                    },
                    colorAxis: {
                        min: 0
                    },
                    series: [
                        {
                            data: seriesData,
                            mapData: Highcharts.maps['custom/world'],
                            joinBy: ['hc-a2', 'country_code'],
                            name: seriesName,
                            states: {
                                hover: {
                                    color: '#D2167A'
                                }
                            },
                            dataLabels: {
                                enabled: true,
                                format: '{point.name}'
                            }
                        }
                    ]
                });
            }

        });

        return WorldMapView;
    }
);
