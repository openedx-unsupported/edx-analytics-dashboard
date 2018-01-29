define(function(require) {
    'use strict';

    var Backbone = require('backbone'),

        FieldFilter = require('course-list/common/filters/field-filter');

    describe('Filters', function() {
        var collection;

        beforeEach(function() {
            var models = [
                new Backbone.Model({
                    animal: 'dog',
                    color: 'brown'
                }),
                new Backbone.Model({
                    animal: 'cat',
                    color: 'orange'
                })
            ];
            collection = new Backbone.Collection(models);
        });

        it('filters by attribute', function() {
            var filter = new FieldFilter('animal', 'dog'),
                results;
            expect(collection.models.length).toEqual(2);
            results = filter.filter(collection);
            expect(results.length).toEqual(1);
            expect(results[0].get('animal')).toEqual('dog');
        });
    });
});
