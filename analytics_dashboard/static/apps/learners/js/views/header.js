/**
 * Renders a section title and last updated date for the learner.
 */
define([
    'marionette',
    'text!learners/templates/header.underscore',
    'underscore',
    'utils/utils'
], function (Marionette, headerTemplate, _, Utils) {
    'use strict';

    var HeaderView = Marionette.ItemView.extend({

        template: _.template(headerTemplate),

        modelEvents: {
            change: 'render'
        },

        templateHelpers: function () {
            var lastUpdatedMessage = _.template(gettext('Date Last Updated: <%- lastUpdatedDateString %>')),
                lastUpdatedDateString = this.model.has('lastUpdated') ?
                    Utils.formatDate(this.model.get('lastUpdated')) :
                    gettext('unknown');
            return {
                title: this.model.get('title'),
                lastUpdated: lastUpdatedMessage({lastUpdatedDateString: lastUpdatedDateString})
            };
        }

    });

    return HeaderView;
});
