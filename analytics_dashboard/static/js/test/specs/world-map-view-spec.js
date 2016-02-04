define(['d3', 'models/course-model', 'views/world-map-view'], function(d3, CourseModel, WorldMapView) {
    'use strict';

    describe('World map view', function () {
        it('should have a popup template', function () {
            var model = new CourseModel(),
                view = new WorldMapView({
                    model: model
                }),
                actual;

            actual = view.popupTemplate({
                name: 'My Map',
                value: 100,
                percent: '100%'
            });
            expect(actual).toBe('<div class="hoverinfo">My Map: 100 (100%)&rlm;</div>');
        });

        it('should format data for Datamaps', function () {
            var rawData = [
                    {countryCode: 'USA', count: 100, percent: 0.3333},
                    {countryCode: 'ARG', count: 200, percent: 0.6666}],
                model = new CourseModel({mapData: rawData}),
                view = new WorldMapView({
                    model: model,
                    modelAttribute: 'mapData'
                }),
                actual,
                expected;

            actual = view.formatData();
            expected = {
                USA: { value: 100, fillKey: 'USA', percent: 0.3333 },
                ARG: { value: 200, fillKey: 'ARG', percent: 0.6666 }
            };
            expect(actual).toEqual(expected);
        });

        it('should fill in colors for countries', function () {
            var lowColor = '#000000',
                highColor = '#ffffff',
                countryData = {
                    USA: { value: 0, fillKey: 'USA' },
                    BLV: { value: 100, fillKey: 'BLV' },
                    ARG: { value: 200, fillKey: 'ARG' }},
                view = new WorldMapView({
                    model: new CourseModel(),
                    lowColor: lowColor,
                    highColor: highColor
                }),
                actual,
                expected,
                colorMap = d3.scale.sqrt()
                    .domain([0, 200])
                    .range([lowColor, highColor]);

            actual = view.getFills(countryData, 200);
            expected = {
                defaultFill: '#000000',
                USA: '#000000',
                BLV: colorMap(100),
                ARG: '#ffffff'
            };
            expect(actual).toEqual(expected);
        });

        it('should return the maximum value', function () {
            var countryData = {
                    USA: { value: 0, fillKey: 'USA' },
                    BLV: { value: 100, fillKey: 'BLV' },
                    ARG: { value: 200, fillKey: 'ARG' }},
                view = new WorldMapView({
                    model: new CourseModel(),
                    modelAttribute: 'mapData'
                }),
                actual;

            actual = view.getCountryMax(countryData);
            expect(actual).toEqual(200);
        });
    });
});
