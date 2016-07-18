define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        Utils = require('utils/utils');

    return Marionette.ItemView.extend({

        template: _.template(gettext('Activity between <%- startDate %> - <%- endDate %>')),

        templateHelpers: function() {
            var dateRange = this.model.get('engagement_ranges').date_range,
                // Translators: 'n/a' means 'not available'
                naText = gettext('n/a');

            return {
                startDate: _(dateRange).has('start') ? Utils.formatDate(dateRange.start) : naText,
                endDate: _(dateRange).has('end') ? Utils.formatDate(dateRange.end) : naText
            };
        }
    });
});
