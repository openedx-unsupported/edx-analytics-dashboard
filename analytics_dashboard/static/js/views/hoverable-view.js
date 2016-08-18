define(['underscore', 'backbone'],
    function(_, Backbone) {
        'use strict';

        /**
         * Use this for triggering track events when an element is hovered over.
         * 'segment:track' and an event are fired when the element is hovered over.
         */
        var HoverableView = Backbone.View.extend({

            initialize: function(options) {
                var self = this;
                self.options = options;
            },

            render: function() {
                var self = this;

                // track the hover
                self.$el.hover(function(event) {
                    var triggered = self.$el.attr('data-track-triggered');
                    if (triggered === undefined || triggered === 'false') {
                        // track this event type along with properties
                        self.model.trigger('segment:track',
                            self.options.trackEventType,
                            self.options.trackProperties);
                        // Only trigger hover once per page load
                        self.$el.attr('data-track-triggered', 'true');
                        self.$el.unbind(event);
                    }
                });

                return this;
            },

            renderIfHasEventType: function() {
                var self = this;

                if (_(self.options).has('trackEventType')) {
                    self.render();
                }
            }

        });

        return HoverableView;
    }
);
