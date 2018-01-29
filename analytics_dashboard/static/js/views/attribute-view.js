define(['views/attribute-listener-view'],
    function(AttributeListenerView) {
        'use strict';

        /**
         * Displays the model attribute as text in the el.
         */
        var AttributeView = AttributeListenerView.extend({

            initialize: function(options) {
                var self = this;
                AttributeListenerView.prototype.initialize.call(this, options);
                self.renderIfDataAvailable();
            },

            render: function() {
                var self = this;
                AttributeListenerView.prototype.render.call(this);
                self.$el.html(self.model.get(self.modelAttribute));
                return self;
            }

        });

        return AttributeView;
    }
);
