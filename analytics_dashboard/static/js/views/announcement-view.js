define(['backbone', 'jquery'], (Backbone, $) => {
  'use strict';

  const AnnouncementView = Backbone.View.extend({
    events: {
      'click .dismiss': 'dismiss',
    },

    initialize() {
      this.csrftoken = $('input[name=csrfmiddlewaretoken]', this.$el).val();
    },

    render() {
      this.delegateEvents();
      return this;
    },

    dismiss() {
      const self = this;
      const url = this.$el.data('dismiss-url');

      $.ajaxSetup({
        beforeSend(xhr) {
          xhr.setRequestHeader('X-CSRFToken', self.csrftoken);
        },
        // Prevent XSS attack in jQuery 2.X:
        // https://github.com/jquery/jquery/issues/2432#issuecomment-140038536
        contents: {
          javascript: false,
        },
      });

      // Record the dismissal on the server.
      if (url) {
        $.post(url);
      }

      // Remove the DOM elements
      self.remove();

      return true;
    },
  });

  return AnnouncementView;
});
