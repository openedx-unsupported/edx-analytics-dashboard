define(['d3', 'models/course-model', 'views/world-map-view'], (d3, CourseModel, WorldMapView) => {
  'use strict';

  describe('World map view', () => {
    it('should have a popup template', () => {
      const model = new CourseModel();
      const view = new WorldMapView({
        model,
      });

      view.renderIfDataAvailable();
      const actual = view.popupTemplate({
        name: 'My Map',
        value: 100,
        percent: '100%',
      });
      expect(actual).toBe('<div class="hoverinfo">My Map: 100 (100%)&rlm;</div>');
    });

    it('should format data for Datamaps', () => {
      const rawData = [
        { countryCode: 'USA', count: 100, percent: 0.3333 },
        { countryCode: 'ARG', count: 200, percent: 0.6666 }];
      const model = new CourseModel({ mapData: rawData });
      const view = new WorldMapView({
        model,
        modelAttribute: 'mapData',
      });

      view.renderIfDataAvailable();
      const actual = view.formatData();
      const expected = {
        USA: {
          value: 100, fillKey: 'USA', percent: 0.3333, name: undefined,
        },
        ARG: {
          value: 200, fillKey: 'ARG', percent: 0.6666, name: undefined,
        },
      };
      expect(actual).toEqual(expected);
    });

    it('should fill in colors for countries', () => {
      const lowColor = '#000000';
      const highColor = '#ffffff';
      const countryData = {
        USA: { value: 0, fillKey: 'USA' },
        BLV: { value: 100, fillKey: 'BLV' },
        ARG: { value: 200, fillKey: 'ARG' },
      };
      const view = new WorldMapView({
        model: new CourseModel(),
        lowColor,
        highColor,
      });
      const colorMap = d3.scale.sqrt()
        .domain([0, 200])
        .range([lowColor, highColor]);

      view.renderIfDataAvailable();
      const actual = view.getFills(countryData, 200);
      const expected = {
        defaultFill: '#000000',
        USA: '#000000',
        BLV: colorMap(100),
        ARG: '#ffffff',
      };
      expect(actual).toEqual(expected);
    });

    it('should return the maximum value', () => {
      const countryData = {
        USA: { value: 0, fillKey: 'USA' },
        BLV: { value: 100, fillKey: 'BLV' },
        ARG: { value: 200, fillKey: 'ARG' },
      };
      const view = new WorldMapView({
        model: new CourseModel(),
        modelAttribute: 'mapData',
      });

      view.renderIfDataAvailable();
      const actual = view.getCountryMax(countryData);
      expect(actual).toEqual(200);
    });
  });
});
