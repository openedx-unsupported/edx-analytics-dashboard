define(
  ['views/attribute-listener-view'],
  (AttributeListenerView) => {
    'use strict';

    /**
         * Displays the model attribute as text in the el.
         */
    const AttributeView = AttributeListenerView.extend({

      initialize(options) {
        const self = this;
        AttributeListenerView.prototype.initialize.call(this, options);
        self.renderIfDataAvailable();
      },

      render() {
        const self = this;
        AttributeListenerView.prototype.render.call(this);
        self.$el.html(self.model.get(self.modelAttribute));
        return self;
      },

    });

    return AttributeView;
  },
);
