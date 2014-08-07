define(['backbone', 'jquery'],
    function (Backbone, $) {
        'use strict';

        /**
         * Given a model and attribute, this View simply renders the value of the model's attribute
         * in the view's element whenever the attribute is changed.
         */
        var SimpleModelAttributeView = Backbone.View.extend({
            initialize: function (options) {
                this.modelAttribute = options.modelAttribute;
                this.listenTo(this.model, 'change:' + this.modelAttribute, this.render);
            },

            render: function () {
                this.$el.html(this.model.get(this.modelAttribute));

                return this;
            }

        });

        return SimpleModelAttributeView;
    }
);
