define((require) => {
  'use strict';

  const Backbone = require('backbone');

  const FieldFilter = require('course-list/common/filters/field-filter');

  describe('Filters', () => {
    let collection;

    beforeEach(() => {
      const models = [
        new Backbone.Model({
          animal: 'dog',
          color: 'brown',
        }),
        new Backbone.Model({
          animal: 'cat',
          color: 'orange',
        }),
      ];
      collection = new Backbone.Collection(models);
    });

    it('filters by attribute', () => {
      const filter = new FieldFilter('animal', 'dog');
      expect(collection.models.length).toEqual(2);
      const results = filter.filter(collection);
      expect(results.length).toEqual(1);
      expect(results[0].get('animal')).toEqual('dog');
    });
  });
});
