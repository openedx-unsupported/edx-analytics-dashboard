define((require) => {
  'use strict';

  const Backbone = require('backbone');

  const SearchFilter = require('course-list/common/filters/search-filter');

  describe('Filters', () => {
    let collection;

    beforeEach(() => {
      const models = [
        new Backbone.Model({
          weather: 'Partly Sunny',
        }),
        new Backbone.Model({
          weather: 'Partly cloudy',
        }),
        new Backbone.Model({
          weather: 'Full Sun',
        })];
      collection = new Backbone.Collection(models);
    });

    it('searches collection', () => {
      const matcher = function (model) {
        return /^Partly/i.test(model.get('weather'));
      };

      const filter = new SearchFilter(matcher);
      expect(collection.models.length).toEqual(3);
      const results = filter.filter(collection);
      expect(results.length).toEqual(2);
      expect(results[0].get('weather')).toEqual('Partly Sunny');
      expect(results[1].get('weather')).toEqual('Partly cloudy');
    });
  });
});
