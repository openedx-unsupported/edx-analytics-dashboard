define(['backbone', 'jquery'],
    function (Backbone, $) {
        'use strict';

        /**
         * This base view listens for a change in a model attribute and calls
         * render() when the attribute changes.  By default, it clears out the
         * view.
         */
        var AttributeListenerView = Backbone.View.extend({
            initialize: function (options) {
                this.modelAttribute = options.modelAttribute;
                this.listenTo(this.model, 'change:' + this.modelAttribute, this.render);
            },

            /**
             * Clears out the view.
             */
            render: function () {
                var self = this;
                self.$el.empty();
                return self;
            }

        });

        return AttributeListenerView;
    }
);
