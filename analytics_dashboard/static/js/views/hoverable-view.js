define(
  ['underscore', 'backbone'],
  (_, Backbone) => {
    'use strict';

    /**
         * Use this for triggering track events when an element is hovered over.
         * 'segment:track' and an event are fired when the element is hovered over.
         */
    const HoverableView = Backbone.View.extend({

      initialize(options) {
        const self = this;
        self.options = options;
      },

      render() {
        const self = this;

        // track the hover
        self.$el.one('mouseenter', () => {
          // track this event type along with properties
          self.model.trigger(
            'segment:track',
            self.options.trackEventType,
            self.options.trackProperties,
          );
        });

        return this;
      },

      renderIfHasEventType() {
        const self = this;

        if (_(self.options).has('trackEventType')) {
          self.render();
        }
      },

    });

    return HoverableView;
  },
);
