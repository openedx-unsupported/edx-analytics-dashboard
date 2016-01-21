define([
    'marionette',
    'text!learners/templates/error.underscore',
    'underscore'
], function (Marionette, errorTemplate, _) {
    'use strict';

    var ErrorView = Marionette.ItemView.extend({
        template: _.template(errorTemplate),
        initialize: function (options) {
            this.options = options || {};
        },
        templateHelpers: function () {
            return this.options;
        }
    });

    return ErrorView;
});
