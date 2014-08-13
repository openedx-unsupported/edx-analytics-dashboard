define(['models/course-model', 'views/world-map-view'], function(CourseModel, WorldMapView) {
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
                value: 100
            });
            expect(actual).toBe('<div class="hoverinfo">My Map: 100</div>');
        });

        it('should format data for Datamaps', function () {
            var rawData = [
                    {countryCode: 'USA', count: 100},
                    {countryCode: 'ARG', count: 200}],
                model = new CourseModel({mapData: rawData}),
                view = new WorldMapView({
                    model: model,
                    modelAttribute: 'mapData'
                }),
                actual,
                expected;

            actual = view.formatData();
            expected = {
                USA: { value: 100, fillKey: 'USA' },
                ARG: { value: 200, fillKey: 'ARG' }
            };
            expect(actual).toEqual(expected);
        });

        it('should fill in colors for countries', function () {
            var countryData = {
                    USA: { value: 0, fillKey: 'USA' },
                    BLV: { value: 100, fillKey: 'BLV' },
                    ARG: { value: 200, fillKey: 'ARG' }},
                view = new WorldMapView({
                    model: new CourseModel(),
                    lowColor: '#000000',
                    highColor: '#ffffff'
                }),
                actual,
                expected;

            actual = view.getFills(countryData, 200);
            expected = {
                defaultFill: '#000000',
                USA: '#000000',
                BLV: '#808080',
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
