define(function(require) {
    'use strict';

    var Backbone = require('backbone'),

        SearchFilter = require('course-list/common/filters/search-filter');

    describe('Filters', function() {
        var collection;

        beforeEach(function() {
            var models = [
                new Backbone.Model({
                    weather: 'Partly Sunny'
                }),
                new Backbone.Model({
                    weather: 'Partly cloudy'
                }),
                new Backbone.Model({
                    weather: 'Full Sun'
                })];
            collection = new Backbone.Collection(models);
        });

        it('searches collection', function() {
            var matcher = function(model) {
                    var regex = new RegExp('^Partly', 'i');
                    return regex.test(model.get('weather'));
                },
                filter,
                results;

            filter = new SearchFilter(matcher);
            expect(collection.models.length).toEqual(3);
            results = filter.filter(collection);
            expect(results.length).toEqual(2);
            expect(results[0].get('weather')).toEqual('Partly Sunny');
            expect(results[1].get('weather')).toEqual('Partly cloudy');
        });
    });
});
