define(['views/hoverable-view'], (HoverableView) => {
  'use strict';

  describe('Hoverable views', () => {
    it('should fire event when hovered', () => {
      const model = { trigger: jasmine.createSpy('trigger') };
      let view = new HoverableView({
        model,
        el: document.createElement('a'),
        trackEventType: 'my:event',
      });

      view.render();

      // the click event should have in turn fired a segment:track event
      view.$el.trigger('mouseenter');
      expect(model.trigger)
        .toHaveBeenCalledWith('segment:track', 'my:event', undefined);

      view = new HoverableView({
        model,
        el: document.createElement('a'),
        trackEventType: 'my:event',
        trackProperties: { 'my-prop': 'a property' },
      });
      view.render();
      view.$el.trigger('mouseenter');
      expect(model.trigger)
        .toHaveBeenCalledWith('segment:track', 'my:event', { 'my-prop': 'a property' });

      // should only fire one event per page load
      model.trigger.calls.reset();
      view.$el.trigger('mouseenter');
      expect(model.trigger.calls.any()).toEqual(false);
    });
  });
});
