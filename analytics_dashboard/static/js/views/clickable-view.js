define(
  ['underscore', 'backbone'],
  (_, Backbone) => {
    'use strict';

    /**
         * Use this for triggering track events when an element is clicked.
         * 'segment:track' and an event are fired when the element is clicked.
         */
    const ClickableView = Backbone.View.extend({

      initialize(options) {
        const self = this;
        self.options = options;
      },

      render() {
        const self = this;

        // track the click
        self.$el.click(() => {
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

    return ClickableView;
  },
);
