define(['views/clickable-view'], (ClickableView) => {
  'use strict';

  describe('Clickable views', () => {
    it('should fire event when clicked', () => {
      const model = { trigger: jasmine.createSpy('trigger') };
      let view = new ClickableView({
        model,
        el: document.createElement('a'),
        trackEventType: 'my:event',
      });

      view.render();

      // the click event should have in turn fired a segment:track event
      view.$el.click();
      expect(model.trigger)
        .toHaveBeenCalledWith('segment:track', 'my:event', undefined);

      view = new ClickableView({
        model,
        el: document.createElement('a'),
        trackEventType: 'my:event',
        trackProperties: { 'my-prop': 'a property' },
      });
      view.render();
      view.$el.click();
      expect(model.trigger)
        .toHaveBeenCalledWith('segment:track', 'my:event', { 'my-prop': 'a property' });
    });
  });
});
