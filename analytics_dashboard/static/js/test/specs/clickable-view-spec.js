define(['views/clickable-view'], function(ClickableView) {
    'use strict';

    describe('Clickable views', function () {
        it('should fire event when clicked', function () {
            var model = { trigger: jasmine.createSpy('trigger') },
                view = new ClickableView({
                    model: model,
                    el: document.createElement('a'),
                    trackEventType: 'my:event'
                });

            view.render();

            // the click event should have in turn fired a segment:track event
            view.$el.click();
            expect(model.trigger)
                .toHaveBeenCalledWith('segment:track', 'my:event', undefined);

            view = new ClickableView({
                model: model,
                el: document.createElement('a'),
                trackEventType: 'my:event',
                trackProperties: {'my-prop': 'a property'}
            });
            view.render();
            view.$el.click();
            expect(model.trigger)
                .toHaveBeenCalledWith('segment:track', 'my:event', {'my-prop': 'a property'});
        });

    });
});
