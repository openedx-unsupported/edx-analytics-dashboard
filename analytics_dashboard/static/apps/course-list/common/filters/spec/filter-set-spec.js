define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backbone = require('backbone'),

        FieldFilter = require('course-list/common/filters/field-filter'),
        FilterSet = require('course-list/common/filters/filter-set');

    describe('Filters', function() {
        var collection;

        beforeEach(function() {
            var models = [
                new Backbone.Model({
                    animal: 'dog',
                    color: 'brown'
                }),
                new Backbone.Model({
                    animal: 'dog',
                    color: 'orange'
                }),
                new Backbone.Model({
                    animal: 'cat',
                    color: 'orange'
                }),
                new Backbone.Model({
                    animal: 'zebra',
                    color: 'black and white'
                })
            ];
            collection = new Backbone.Collection(models);
        });

        it('applies AND filter', function() {
            var filterDog = new FieldFilter('animal', 'dog'),
                orangeFilter = new FieldFilter('color', 'orange'),
                filterSet = new FilterSet('AND', [filterDog, orangeFilter]),
                results;
            expect(collection.models.length).toEqual(4);
            results = filterSet.filter(collection);
            expect(results.length).toEqual(1);
            expect(results[0].get('animal')).toEqual('dog');
            expect(results[0].get('color')).toEqual('orange');
        });

        it('applies OR filter', function() {
            var filterDog = new FieldFilter('animal', 'dog'),
                orangeFilter = new FieldFilter('color', 'orange'),
                filterSet = new FilterSet('OR', [filterDog, orangeFilter]),
                results;
            expect(collection.models.length).toEqual(4);
            results = filterSet.filter(collection);
            expect(results.length).toEqual(3);

            // this OR will get everything but the zebra
            _(results).each(function(result) {
                expect(_(['dog', 'cat']).contains(result.get('animal'))).toBe(true);
                expect(_(['orange', 'brown']).contains(result.get('color'))).toBe(true);
            });
        });

        it('throws error', function() {
            expect(function() {
                new FilterSet('not a mode'); // eslint-disable-line no-new
            }).toThrow(new Error('Only valid modes are: AND, OR'));
        });
    });
});
