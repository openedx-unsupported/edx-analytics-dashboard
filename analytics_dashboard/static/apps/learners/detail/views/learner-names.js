define(function (require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette');

    return Marionette.ItemView.extend({
        template: _.template(require('text!learners/detail/templates/learner-names.underscore')),
        modelEvents: {
            change: 'render',
            'change:email': 'render'
        }
    });

});
