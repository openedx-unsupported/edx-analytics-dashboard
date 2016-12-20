/**
 * Renders a section title and last updated date for the learner.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        headerTemplate = require('text!components/header/templates/header.underscore'),

        HeaderView;

    HeaderView = Marionette.ItemView.extend({

        template: _.template(headerTemplate),

        modelEvents: {
            change: 'render'
        },

        templateHelpers: function() {
            return {
                title: this.model.get('title')
            };
        }

    });

    return HeaderView;
});
