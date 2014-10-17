define(['backbone', 'jquery'], function (Backbone, $) {
    'use strict';

    var AnnouncementView = Backbone.View.extend({
        events: {
            'closed.bs.alert': 'dismiss'
        },

        initialize: function () {
            this.csrftoken = $('input[name=csrfmiddlewaretoken]', this.$el).val();
            this.render();
        },

        render: function () {
            this.delegateEvents();
            return this;
        },

        dismiss: function () {
            var self = this,
                url = this.$el.data('dismiss-url');

            $.ajaxSetup({
                beforeSend: function (xhr) {
                    xhr.setRequestHeader('X-CSRFToken', self.csrftoken);
                }
            });

            if (url) {
                $.post(url);
            }
        }
    });

    return AnnouncementView;
});
