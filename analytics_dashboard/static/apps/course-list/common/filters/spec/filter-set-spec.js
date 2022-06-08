define((require) => {
  'use strict';

  const _ = require('underscore');
  const Backbone = require('backbone');

  const FieldFilter = require('course-list/common/filters/field-filter');
  const FilterSet = require('course-list/common/filters/filter-set');

  describe('Filters', () => {
    let collection;

    beforeEach(() => {
      const models = [
        new Backbone.Model({
          animal: 'dog',
          color: 'brown',
        }),
        new Backbone.Model({
          animal: 'dog',
          color: 'orange',
        }),
        new Backbone.Model({
          animal: 'cat',
          color: 'orange',
        }),
        new Backbone.Model({
          animal: 'zebra',
          color: 'black and white',
        }),
      ];
      collection = new Backbone.Collection(models);
    });

    it('applies AND filter', () => {
      const filterDog = new FieldFilter('animal', 'dog');
      const orangeFilter = new FieldFilter('color', 'orange');
      const filterSet = new FilterSet('AND', [filterDog, orangeFilter]);
      expect(collection.models.length).toEqual(4);
      const results = filterSet.filter(collection);
      expect(results.length).toEqual(1);
      expect(results[0].get('animal')).toEqual('dog');
      expect(results[0].get('color')).toEqual('orange');
    });

    it('applies OR filter', () => {
      const filterDog = new FieldFilter('animal', 'dog');
      const orangeFilter = new FieldFilter('color', 'orange');
      const filterSet = new FilterSet('OR', [filterDog, orangeFilter]);
      expect(collection.models.length).toEqual(4);
      const results = filterSet.filter(collection);
      expect(results.length).toEqual(3);

      // this OR will get everything but the zebra
      _(results).each((result) => {
        expect(_(['dog', 'cat']).contains(result.get('animal'))).toBe(true);
        expect(_(['orange', 'brown']).contains(result.get('color'))).toBe(true);
      });
    });

    it('throws error', () => {
      expect(() => {
        new FilterSet('not a mode'); // eslint-disable-line no-new
      }).toThrow(new Error('Only valid modes are: AND, OR'));
    });
  });
});
