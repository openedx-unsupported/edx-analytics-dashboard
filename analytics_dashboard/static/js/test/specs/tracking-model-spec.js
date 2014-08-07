define(['models/tracking-model'], function(TrackingModel) {
    'use strict';

    describe('Tracking model', function () {

        it('should be tracking', function () {
            var model = new TrackingModel({segmentApplicationId: 'test'});
            expect(model.isTracking()).toBe(true);
            expect(model.get('segmentApplicationId')).toBe('test');
        });

        it('should not be tracking', function () {
            var model = new TrackingModel();
            expect(model.isTracking()).toBe(false);

            model.set('segmentApplicationId', null);
            expect(model.isTracking()).toBe(false);
        });
    });
});
