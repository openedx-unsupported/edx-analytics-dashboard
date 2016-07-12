define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette');

    return Marionette.ItemView.extend({
        template: _.template(require('text!learners/detail/templates/email.underscore')),
        modelEvents: {
            'change:email': 'render'
        }
    });
});
