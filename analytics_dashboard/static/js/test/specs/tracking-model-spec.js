define(['models/tracking-model'], (TrackingModel) => {
  'use strict';

  describe('Tracking model', () => {
    it('should be tracking', () => {
      const model = new TrackingModel({ segmentApplicationId: 'test' });
      expect(model.isTracking()).toBe(true);
      expect(model.get('segmentApplicationId')).toBe('test');
    });

    it('should not be tracking', () => {
      const model = new TrackingModel();
      expect(model.isTracking()).toBe(false);

      model.set('segmentApplicationId', null);
      expect(model.isTracking()).toBe(false);
    });
  });
});
