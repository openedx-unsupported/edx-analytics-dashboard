define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette');

    return Marionette.ItemView.extend({
        template: _.template(require('learners/detail/templates/learner-names.underscore')),
        events: {
            'click .learner-email a': 'onEmailClick'
        },
        modelEvents: {
            change: 'render',
            'change:email': 'render'
        },
        onEmailClick: function() {
            this.options.trackingModel.trigger('segment:track', 'edx.bi.learner.email_link_clicked', {});
        }
    });
});
